import pytest

from app.core.config import get_settings
from app.core.errors import AppError
from app.services.llm_client import resolve_api_key


def test_missing_api_key_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(AppError) as exc:
        resolve_api_key(None)

    assert exc.value.code == "missing_openai_api_key"
