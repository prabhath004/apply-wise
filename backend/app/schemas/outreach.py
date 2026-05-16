from pydantic import BaseModel, Field


class OutreachGenerateRequest(BaseModel):
    analysis_id: str
    contact_id: str | None = None
    tone: str = Field(default="concise", pattern="^(concise|friendly|formal)$")
    channel: str = Field(default="email", pattern="^(email|linkedin)$")


class OutreachResponse(BaseModel):
    outreach_id: str | None = None
    subject: str | None = None
    body: str
