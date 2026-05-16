import re
from collections.abc import Iterable


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
WHITESPACE_RE = re.compile(r"\s+")


SKILL_ALIASES: dict[str, str] = {
    "amazon web services": "AWS",
    "aws": "AWS",
    "azure": "Azure",
    "beautifulsoup": "BeautifulSoup",
    "c++": "C++",
    "css": "CSS",
    "docker": "Docker",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "gcp": "GCP",
    "git": "Git",
    "graphql": "GraphQL",
    "html": "HTML",
    "java": "Java",
    "javascript": "JavaScript",
    "kubernetes": "Kubernetes",
    "langchain": "LangChain",
    "machine learning": "Machine Learning",
    "mongodb": "MongoDB",
    "mysql": "MySQL",
    "next.js": "Next.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "python": "Python",
    "pytorch": "PyTorch",
    "react": "React",
    "react.js": "React",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "sql": "SQL",
    "sqlite": "SQLite",
    "tailwind": "Tailwind CSS",
    "tensorflow": "TensorFlow",
    "typescript": "TypeScript",
}


def normalize_whitespace(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def normalize_multiline_text(value: str) -> str:
    lines = [normalize_whitespace(line) for line in value.replace("\r", "\n").split("\n")]
    return "\n".join(line for line in lines if line)


def extract_email(text: str) -> str | None:
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_RE.search(text)
    return normalize_whitespace(match.group(1)) if match else None


def canonical_skill(value: str) -> str:
    key = normalize_whitespace(value).lower()
    return SKILL_ALIASES.get(key, value.strip())


def extract_known_skills(text: str) -> list[str]:
    lowered = text.lower()
    found: set[str] = set()
    for alias, canonical in SKILL_ALIASES.items():
        pattern = rf"(?<![\w+]){re.escape(alias)}(?![\w+])"
        if re.search(pattern, lowered):
            found.add(canonical)
    return sorted(found)


def flatten_skill_groups(skills: dict[str, list[str]] | object) -> list[str]:
    if isinstance(skills, dict):
        values: Iterable[object] = skills.values()
    else:
        values = getattr(skills, "__dict__", {}).values()

    flattened: set[str] = set()
    for group in values:
        if isinstance(group, list):
            for skill in group:
                if isinstance(skill, str) and skill.strip():
                    flattened.add(canonical_skill(skill))
    return sorted(flattened)
