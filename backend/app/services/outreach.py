import json
from typing import Protocol

from pydantic import ValidationError

from app.core.errors import AppError
from app.schemas.analysis import FitScore
from app.schemas.company import CompanyInfo
from app.schemas.contacts import ContactInfo
from app.schemas.outreach import OutreachResponse


class JsonCompletionClient(Protocol):
    async def json_completion(self, system_prompt: str, user_prompt: str) -> dict:
        pass


def _truncate(value: str, limit: int = 10000) -> str:
    if len(value) <= limit:
        return value
    return value[:limit] + "\n[Truncated for model context]"


def generate_local_outreach(
    job_title: str,
    company_name: str,
    fit_score: FitScore,
    company: CompanyInfo,
    contact: ContactInfo | None,
    tone: str,
    channel: str,
) -> tuple[str | None, str]:
    recipient = contact.name if contact else "there"
    subject = None if channel == "linkedin" else f"{job_title} role at {company_name}"

    strengths = fit_score.matching_skills[:3]
    skill_sentence = (
        f"My background lines up with {', '.join(strengths)}."
        if strengths
        else "My background appears relevant to the role, and I would like to learn more."
    )
    company_sentence = (
        f"I was interested in {company.name} after reviewing its public site."
        if company.summary or company.website
        else f"I was interested in the {job_title} opening at {company_name}."
    )
    closer = "Would you be open to pointing me to the right person for this role?"
    if tone == "formal":
        closer = "I would appreciate any guidance on the appropriate hiring contact for this role."
    elif tone == "friendly":
        closer = "I would be grateful for any guidance on whether my background could be a fit."

    body = (
        f"Hi {recipient},\n\n"
        f"{company_sentence} {skill_sentence} "
        f"The fit analysis surfaced a {fit_score.recommendation.lower()} recommendation, "
        "so I am reaching out with a focused note rather than a generic application message.\n\n"
        f"{closer}\n\n"
        "Best,\n"
    )
    if channel == "linkedin" and len(body) > 600:
        body = body[:597].rstrip() + "..."
    return subject, body


async def generate_openai_outreach(
    llm_client: JsonCompletionClient,
    resume_text: str,
    job_title: str,
    company_name: str,
    job_description: str,
    fit_score: FitScore,
    company: CompanyInfo,
    contact: ContactInfo | None,
    tone: str,
    channel: str,
) -> tuple[str | None, str]:
    system_prompt = """
You write concise, professional job outreach for an early-career technical job seeker.
Return only valid JSON. Do not include markdown.

Rules:
- Do not exaggerate the candidate's experience.
- Do not claim the candidate spoke with the recipient.
- Do not mention visa status unless explicitly present in provided context as something the user wants to mention.
- Do not invent company facts, recruiter facts, personal relationships, metrics, or achievements.
- No emojis.
- Email body should usually be 120-180 words.
- LinkedIn body should usually be 400-600 characters.
- Use simple professional English.
- Personalize from the resume, job description, fit score, company summary, and contact role when evidence exists.
""".strip()

    user_prompt = json.dumps(
        {
            "expected_json_shape": {
                "subject": f"{job_title} role at {company_name}" if channel == "email" else None,
                "body": "Hi ...",
            },
            "channel": channel,
            "tone": tone,
            "job": {
                "job_title": job_title,
                "company_name": company_name,
                "job_description": _truncate(job_description, 8000),
            },
            "resume_text": _truncate(resume_text),
            "fit_score": fit_score.model_dump(),
            "company": company.model_dump(),
            "contact": contact.model_dump() if contact else None,
        },
        ensure_ascii=True,
    )

    raw = await llm_client.json_completion(system_prompt, user_prompt)
    try:
        message = OutreachResponse.model_validate(raw)
    except ValidationError as exc:
        raise AppError(
            "invalid_outreach_response",
            "OpenAI returned outreach that did not match the expected schema.",
            status_code=502,
        ) from exc

    subject = message.subject if channel == "email" else None
    body = message.body.strip()
    if not body:
        raise AppError("empty_outreach_response", "OpenAI returned an empty outreach message.", status_code=502)
    return subject, body
