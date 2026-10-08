import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do .env na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEV_COMMUNITY_USER = os.getenv("DEVCommunity_user", "")
DEV_COMMUNITY_API_KEY = os.getenv("DEVCommunity_API_Keys", "")
GITHUB_KEY = os.getenv("GITHUB_KEY", "")

RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
