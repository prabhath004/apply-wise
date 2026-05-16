from pydantic import BaseModel, Field, HttpUrl


class SourceLink(BaseModel):
    title: str
    url: str


class CompanyInfo(BaseModel):
    name: str
    summary: str | None = None
    industry: str | None = None
    website: str | None = None
    careers_url: str | None = None
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceLink] = Field(default_factory=list)
