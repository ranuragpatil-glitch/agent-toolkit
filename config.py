# config.py
import os
from pathlib import Path

from dotenv import load_dotenv

# Load the project-local environment file without ever committing it.
ROOT = Path(__file__).parent.resolve()
load_dotenv(ROOT / ".env")

# ---------- Paths ----------
WORKSPACE = ROOT / "workspace"
MEMORY_DIR = ROOT / "memory"
CODE_INDEX_DIR = ROOT / "code_index"

WORKSPACE.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)
CODE_INDEX_DIR.mkdir(exist_ok=True)

# ---------- Model ----------
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise RuntimeError("NVIDIA_API_KEY is missing from the project environment")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
TEMPERATURE = 0.2

# ---------- Agent ----------
MAX_RETRIES = 3
MAX_SEARCH_RESULTS = 5
MAX_MEMORY_RESULTS = 3
MAX_CODE_RESULTS = 5

# ---------- Sandbox ----------
SANDBOX_TIMEOUT = 30          # seconds
SHELL_ALLOWLIST = {"ls", "cat", "pytest", "ruff", "python", "git"}

# ---------- Memory ----------
MEMORY_COLLECTION = "decisions"
CODE_COLLECTION = "code_chunks"
