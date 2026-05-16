from pydantic import BaseModel, Field

from app.schemas.company import CompanyInfo
from app.schemas.contacts import ContactInfo
from app.schemas.job import JobInput


class ScoreBreakdown(BaseModel):
    skills: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    seniority: int = Field(ge=0, le=100)
    domain: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)


class FitScore(BaseModel):
    overall: int = Field(ge=0, le=100)
    recommendation: str
    breakdown: ScoreBreakdown
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class AnalyzeJobRequest(BaseModel):
    resume_id: str
    job: JobInput


class AnalyzeJobResponse(BaseModel):
    analysis_id: str
    job_id: str
    fit_score: FitScore
    company: CompanyInfo
    contacts: list[ContactInfo] = Field(default_factory=list)
