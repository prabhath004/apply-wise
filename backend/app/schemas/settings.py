from pydantic import BaseModel


class SettingsRequest(BaseModel):
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"
    persist_api_key: bool = False


class SettingsResponse(BaseModel):
    saved: bool
    persisted_api_key: bool = False
