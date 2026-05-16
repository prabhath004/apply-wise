from functools import lru_cache
from pathlib import Path
import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"


class Settings(BaseModel):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    database_url: str = f"sqlite:///{DATA_DIR / 'applyintel.db'}"
    cors_origins: list[str] = ["http://localhost:5173"]
    cors_origin_regex: str | None = r"chrome-extension://.*"


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173"]
    return [part.strip() for part in value.split(",") if part.strip() and "*" not in part]


@lru_cache
def get_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    persisted: dict[str, str] = {}
    if SETTINGS_FILE.exists():
        persisted = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY") or persisted.get("openai_api_key") or None,
        openai_model=os.getenv("OPENAI_MODEL", persisted.get("openai_model", "gpt-4.1-mini")),
        embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            persisted.get("embedding_model", "text-embedding-3-small"),
        ),
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'applyintel.db'}"),
        cors_origins=_split_csv(os.getenv("BACKEND_CORS_ORIGINS")),
    )
