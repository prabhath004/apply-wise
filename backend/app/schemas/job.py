from pydantic import BaseModel, Field, field_validator


class JobInput(BaseModel):
    source: str = "manual"
    job_title: str
    company_name: str
    location: str | None = None
    job_url: str | None = None
    job_description: str
    employment_type: str | None = None
    seniority: str | None = None
    posted_date: str | None = None

    @field_validator("job_title", "company_name", "job_description")
    @classmethod
    def require_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty")
        return cleaned


class VisaSignals(BaseModel):
    mentions_sponsorship: bool = False
    mentions_no_sponsorship: bool = False
    mentions_us_citizenship: bool = False


class ParsedJob(BaseModel):
    role_category: str | None = None
    seniority: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    years_experience_min: int | None = None
    years_experience_max: int | None = None
    domain: str | None = None
    clearance_required: bool = False
    visa_signals: VisaSignals = Field(default_factory=VisaSignals)
