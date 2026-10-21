# main.py
import argparse
import json

from agent import run_agent
from memory import recall
from tools import list_tools


def print_result(result: dict):
    print("\n" + "=" * 60)
    print("FINAL CODE")
    print("=" * 60)
    print(result.get("code", "(no code generated)"))

    print("\n" + "=" * 60)
    print(f"STATUS: {'DONE' if result['done'] else 'INCOMPLETE'}")
    print(f"RETRIES: {result['retries']}")
    print(f"TOOL CALLS: {len(result.get('tool_calls', []))}")
    print("=" * 60)

    if result.get("errors"):
        print("\nERRORS:")
        for e in result["errors"]:
            print(f"  - {e}")

    if result.get("tool_results"):
        print("\nTOOL RESULTS:")
        for tr in result["tool_results"]:
            status = "✓" if tr["result"].get("ok") else "✗"
            print(f"  {status} {tr['tool']}({list(tr['args'].keys())})")


def main():
    parser = argparse.ArgumentParser(description="Free Stack Coding Agent")
    parser.add_argument("task", nargs="*", help="Task for the agent")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--recall", type=str, help="Recall from memory")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # --list-tools
    if args.list_tools:
        print("Available tools:")
        for t in list_tools():
            print(f"  - {t}")
        return

    # --recall
    if args.recall:
        r = recall(args.recall)
        if r["ok"]:
            for i, doc in enumerate(r["results"], 1):
                print(f"{i}. {doc}")
        else:
            print(f"Error: {r['error']}")
        return

    # Task run
    if not args.task:
        parser.print_help()
        return

    task = " ".join(args.task)
    print(f"📝 Task: {task}\n")
    print("🧠 Thinking... (planner → coder → tools → reflect)")

    result = run_agent(task)

    if args.json:
        # tool_results ko stringify karo (JSON-safe)
        safe = {k: v for k, v in result.items() if k != "tool_results"}
        safe["tool_results"] = [
            {"tool": tr["tool"], "args": tr["args"], "ok": tr["result"].get("ok")}
            for tr in result.get("tool_results", [])
        ]
        print(json.dumps(safe, indent=2, default=str))
    else:
        print_result(result)


if __name__ == "__main__":
    main()