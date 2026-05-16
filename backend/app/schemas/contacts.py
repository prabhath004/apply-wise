from pydantic import BaseModel, Field

from app.schemas.company import SourceLink


class ContactInfo(BaseModel):
    id: str | None = None
    name: str
    title: str | None = None
    profile_url: str | None = None
    email: str | None = None
    email_type: str | None = None
    confidence: int = Field(ge=0, le=100)
    confidence_reason: str | None = None
    sources: list[SourceLink] = Field(default_factory=list)
