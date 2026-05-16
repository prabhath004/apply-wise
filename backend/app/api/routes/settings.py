import json

from fastapi import APIRouter

from app.core.config import DATA_DIR, SETTINGS_FILE, get_settings
from app.schemas.settings import SettingsRequest, SettingsResponse
from app.utils.security import mask_secret


router = APIRouter(prefix="/settings", tags=["settings"])


@router.post("", response_model=SettingsResponse)
def save_settings(payload: SettingsRequest) -> SettingsResponse:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    persisted_api_key = bool(payload.openai_api_key and payload.persist_api_key)
    settings = {
        "openai_model": payload.openai_model,
        "embedding_model": payload.embedding_model,
        "api_key_preview": mask_secret(payload.openai_api_key),
    }
    if persisted_api_key:
        settings["openai_api_key"] = payload.openai_api_key

    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    get_settings.cache_clear()
    return SettingsResponse(saved=True, persisted_api_key=persisted_api_key)
