from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    school: str
    degree: str | None = None
    graduation_date: str | None = None


class SkillGroups(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    cloud: list[str] = Field(default_factory=list)
    databases: list[str] = Field(default_factory=list)
    ai_ml: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    company: str
    title: str
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ParsedResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    education: list[EducationItem] = Field(default_factory=list)
    skills: SkillGroups = Field(default_factory=SkillGroups)
    experience: list[ExperienceItem] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    parser_notes: list[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    resume_id: str
    name: str | None = None
    parsed_profile: ParsedResumeProfile
