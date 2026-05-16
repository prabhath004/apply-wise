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
    public_emails: list[str] = Field(default_factory=list)
    email_pattern: str | None = None
    email_domain: str | None = None
    h1b_data_url: str | None = None
    h1b_summary: str | None = None
    recruiter_search_urls: list[SourceLink] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    sources: list[SourceLink] = Field(default_factory=list)
