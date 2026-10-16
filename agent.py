# agent.py
from typing import TypedDict, Literal, Annotated
import operator

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL, TEMPERATURE, MAX_RETRIES 
from prompts import PLANNER_PROMPT, CODER_PROMPT, TOOL_ROUTER_PROMPT, REFLECT_PROMPT
from utils import extract_code_block, format_errors, truncate
from tools import execute_tool, list_tools


# ---------- State ----------
class AgentState(TypedDict):
    task: str
    plan: str
    code: str
    tool_calls: list
    tool_results: Annotated[list, operator.add]
    errors: Annotated[list, operator.add]
    retries: int
    done: bool


# ---------- LLM ----------
llm = ChatOpenAI(
    model=NVIDIA_MODEL,
    base_url=NVIDIA_BASE_URL,
    api_key=NVIDIA_API_KEY,
    temperature=TEMPERATURE,
    max_tokens=4096,
)


# ---------- Structured Schemas ----------
ToolName = Literal[
    "read_file", "write_file", "edit_file", "list_files",
    "run_code", "safe_shell",
    "web_search", "fetch_page",
    "remember", "recall", "index_code_file", "search_code",
]


class ToolCall(BaseModel):
    tool: ToolName
    args: dict = Field(default_factory=dict)
    reason: str = ""


class ToolPlan(BaseModel):
    calls: list[ToolCall] = Field(default_factory=list)
    final_answer: str | None = None


# ---------- Nodes ----------
def planner_node(state: AgentState) -> dict:
    """Step 1: Plan banao."""
    msg = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=(
            f"Task: {state['task']}\n\n"
            f"Previous errors:\n{format_errors(state['errors'])}"
        )),
    ]
    plan = llm.invoke(msg).content
    return {"plan": plan}


def coder_node(state: AgentState) -> dict:
    """Step 2: Code likho."""
    msg = [
        SystemMessage(content=CODER_PROMPT),
        HumanMessage(content=(
            f"Task: {state['task']}\n\n"
            f"Plan:\n{state['plan']}\n\n"
            f"Errors to fix:\n{format_errors(state['errors'])}"
        )),
    ]
    raw = llm.invoke(msg).content
    return {"code": extract_code_block(raw)}


def tool_router_node(state: AgentState) -> dict:

    """Step 3: Decide + execute tools."""
    structured = llm.with_structured_output(ToolPlan, method="json_schema")
    decision = structured.invoke([
        SystemMessage(content=TOOL_ROUTER_PROMPT),
        HumanMessage(content=(
            f"Task: {state['task']}\n\n"
            f"Code:\n{truncate(state['code'], 1500)}\n\n"
            f"Available tools: {list_tools()}"
        )),
    ]) or ToolPlan()

    # Safety net: task testing maangta hai par model ne run_code nahi bola to khud inject karo
    task_lower = state["task"].lower()
    needs_test = any(k in task_lower for k in ["test", "verify", "run", "check"])
    if needs_test and not any(c.tool == "run_code" for c in decision.calls):
        decision.calls.append(ToolCall(
            tool="run_code",
            args={"code": state["code"]},
            reason="auto-injected: task mentioned tests, model skipped run_code",
        ))
    # ---------- ACTUAL TOOL EXECUTION ----------
    results = []
    errors = []
    last_read_content = None  # read_file ka content yaad rakhne ke liye, run_code ke liye

    for call in decision.calls:
        tool_name = call.tool
        args = dict(call.args)

        # Model kabhi-kabhi reason ko args mein daal deta hai — hatao
        args.pop("reason", None)

        # write_file: content missing ho to state ka code use karo
        if tool_name == "write_file" and not args.get("content"):
            args["content"] = state["code"]

        # run_code: pehle read_file hua ho to uska content, warna state ka code
        if tool_name == "run_code" and "code" not in args:
            args["code"] = last_read_content or state["code"]

        # run_code ke liye sirf allowed keys bhejo (code, mode)
        if tool_name == "run_code":
            args = {k: v for k, v in args.items() if k in ("code", "mode")}

        res = execute_tool(tool_name, args)

        if tool_name == "read_file" and res.get("ok"):
            last_read_content = res.get("content", "")

        results.append({
            "tool": tool_name,
            "args": args,
            "reason": call.reason,
            "result": res,
        })
        if not res.get("ok", False):
            errors.append(f"{tool_name} failed: {res.get('error', 'unknown')}")

    return {
        "tool_calls": [c.model_dump() for c in decision.calls],
        "tool_results": results,
        "errors": errors,
    }


def reflect_node(state: AgentState) -> dict:
    """Step 4: Verdict."""
    recent_errors = state["errors"]
    if not recent_errors:
        return {"done": True}

    new_retries = state["retries"] + 1
    done = new_retries >= MAX_RETRIES
    return {"retries": new_retries, "done": done}


# ---------- Routing ----------
def should_continue(state: AgentState) -> str:
    if state["done"]:
        return "end"
    if state["errors"] and state["retries"] < MAX_RETRIES:
        return "retry"
    return "end"


# ---------- Graph ----------
def build_graph():
    g = StateGraph(AgentState)
    g.add_node("planner", planner_node)
    g.add_node("coder", coder_node)
    g.add_node("tools", tool_router_node)
    g.add_node("reflect", reflect_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "coder")
    g.add_edge("coder", "tools")
    g.add_edge("tools", "reflect")
    g.add_conditional_edges(
        "reflect",
        should_continue,
        {"retry": "planner", "end": END},
    )
    return g.compile()


# ---------- Public API ----------
def run_agent(task: str) -> dict:
    """Task lo, final state return karo."""
    app = build_graph()
    initial: AgentState = {
        "task": task,
        "plan": "",
        "code": "",
        "tool_calls": [],
        "tool_results": [],
        "errors": [],
        "retries": 0,
        "done": False,
    }
    return app.invoke(initial)