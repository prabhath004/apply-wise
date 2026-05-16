from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader

from app.schemas.resume import EducationItem, ParsedResumeProfile, SkillGroups
from app.utils.text import extract_email, extract_known_skills, extract_phone, normalize_multiline_text


LANGUAGE_SKILLS = {"C++", "Java", "JavaScript", "Python", "SQL", "TypeScript"}
FRAMEWORK_SKILLS = {"FastAPI", "Flask", "Next.js", "Node.js", "React", "Tailwind CSS"}
CLOUD_SKILLS = {"AWS", "Azure", "Docker", "GCP", "Kubernetes"}
DATABASE_SKILLS = {"MongoDB", "MySQL", "PostgreSQL", "SQLite"}
AI_ML_SKILLS = {"LangChain", "Machine Learning", "PyTorch", "TensorFlow"}


async def read_resume_upload(file: UploadFile) -> str:
    content = await file.read()
    file_name = file.filename or "resume"
    content_type = file.content_type or ""

    if file_name.lower().endswith(".pdf") or content_type == "application/pdf":
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return normalize_multiline_text("\n".join(pages))

    return normalize_multiline_text(content.decode("utf-8", errors="ignore"))


def _first_likely_name(lines: list[str], email: str | None) -> str | None:
    for line in lines[:8]:
        if not line or "@" in line or any(char.isdigit() for char in line):
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and len(line) <= 80:
            return line
    if email:
        local = email.split("@", 1)[0]
        parts = [part.capitalize() for part in local.replace(".", " ").replace("_", " ").split()]
        if parts:
            return " ".join(parts)
    return None


def _education(lines: list[str]) -> list[EducationItem]:
    keywords = ("university", "college", "institute", "school")
    degree_keywords = ("b.s", "bs", "bachelor", "m.s", "ms", "master", "phd", "computer science")
    items: list[EducationItem] = []
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in keywords):
            degree = line if any(keyword in lowered for keyword in degree_keywords) else None
            items.append(EducationItem(school=line, degree=degree))
    return items[:3]


def _skill_groups(skills: list[str]) -> SkillGroups:
    return SkillGroups(
        languages=sorted(skill for skill in skills if skill in LANGUAGE_SKILLS),
        frameworks=sorted(skill for skill in skills if skill in FRAMEWORK_SKILLS),
        cloud=sorted(skill for skill in skills if skill in CLOUD_SKILLS),
        databases=sorted(skill for skill in skills if skill in DATABASE_SKILLS),
        ai_ml=sorted(skill for skill in skills if skill in AI_ML_SKILLS),
        tools=sorted(
            skill
            for skill in skills
            if skill
            not in LANGUAGE_SKILLS
            | FRAMEWORK_SKILLS
            | CLOUD_SKILLS
            | DATABASE_SKILLS
            | AI_ML_SKILLS
        ),
    )


def parse_resume_text(raw_text: str, used_llm: bool = False) -> ParsedResumeProfile:
    normalized = normalize_multiline_text(raw_text)
    lines = [line for line in normalized.splitlines() if line]
    email = extract_email(normalized)
    skills = extract_known_skills(normalized)
    notes = []
    if not used_llm:
        notes.append("Parsed locally with heuristic extraction. Add an OpenAI API key for richer structuring.")

    return ParsedResumeProfile(
        name=_first_likely_name(lines, email),
        email=email,
        phone=extract_phone(normalized),
        education=_education(lines),
        skills=_skill_groups(skills),
        parser_notes=notes,
    )
