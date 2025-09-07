# src/utils/config.py
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# load .env from project root when scripts run in VS Code
load_dotenv(ROOT / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/genai")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")