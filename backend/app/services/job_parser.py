import re

from app.schemas.job import ParsedJob, VisaSignals
from app.utils.text import extract_known_skills, normalize_multiline_text


ENTRY_LEVEL_TERMS = ("entry level", "new grad", "university graduate", "junior", "software engineer i")
SENIOR_TERMS = ("senior", "staff", "principal", "lead")
CLEARANCE_TERMS = ("security clearance", "top secret", "ts/sci", "secret clearance")
NO_SPONSORSHIP_TERMS = (
    "unable to sponsor",
    "will not sponsor",
    "no sponsorship",
    "without sponsorship",
    "must be authorized to work",
)
SPONSORSHIP_TERMS = ("sponsorship available", "visa sponsorship", "sponsor visas")
US_CITIZENSHIP_TERMS = ("u.s. citizen", "us citizen", "united states citizen")


def _seniority(title: str, description: str) -> str | None:
    text = f"{title}\n{description}".lower()
    if any(term in text for term in SENIOR_TERMS):
        return "senior"
    if any(term in text for term in ENTRY_LEVEL_TERMS):
        return "entry_level"
    if "intern" in text:
        return "internship"
    return None


def _years(text: str) -> tuple[int | None, int | None]:
    matches = [int(value) for value in re.findall(r"(\d+)\+?\s*(?:years|yrs)", text.lower())]
    if not matches:
        return None, None
    return min(matches), max(matches)


def _responsibilities(description: str) -> list[str]:
    lines = normalize_multiline_text(description).splitlines()
    candidates = []
    for line in lines:
        cleaned = line.strip(" -•\t")
        lowered = cleaned.lower()
        if len(cleaned) < 25:
            continue
        if any(term in lowered for term in ("build", "design", "develop", "implement", "maintain", "collaborate")):
            candidates.append(cleaned)
    return candidates[:6]


def parse_job(job_title: str, description: str) -> ParsedJob:
    text = normalize_multiline_text(description)
    lowered = text.lower()
    years_min, years_max = _years(text)
    skills = extract_known_skills(text)
    mentions_no_sponsorship = any(term in lowered for term in NO_SPONSORSHIP_TERMS)

    return ParsedJob(
        role_category="software_engineering" if "software" in f"{job_title} {text}".lower() else None,
        seniority=_seniority(job_title, text),
        required_skills=skills,
        preferred_skills=[],
        responsibilities=_responsibilities(text),
        years_experience_min=years_min,
        years_experience_max=years_max,
        domain="software" if "software" in lowered or "developer" in lowered else None,
        clearance_required=any(term in lowered for term in CLEARANCE_TERMS),
        visa_signals=VisaSignals(
            mentions_sponsorship=not mentions_no_sponsorship and any(term in lowered for term in SPONSORSHIP_TERMS),
            mentions_no_sponsorship=mentions_no_sponsorship,
            mentions_us_citizenship=any(term in lowered for term in US_CITIZENSHIP_TERMS),
        ),
    )
