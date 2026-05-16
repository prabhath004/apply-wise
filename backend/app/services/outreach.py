from app.schemas.analysis import FitScore
from app.schemas.company import CompanyInfo
from app.schemas.contacts import ContactInfo


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
