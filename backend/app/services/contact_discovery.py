from app.schemas.company import CompanyInfo, SourceLink
from app.schemas.contacts import ContactInfo
from app.services.email_patterns import generate_email_from_pattern


RECRUITING_TITLES = (
    "technical recruiter",
    "engineering recruiter",
    "talent acquisition",
    "university recruiter",
    "campus recruiter",
    "hiring manager",
    "engineering manager",
)


def _name_parts(name: str) -> tuple[str, str] | None:
    parts = [part.strip(" ,.") for part in name.split() if part.strip(" ,.")]
    if len(parts) < 2:
        return None
    return parts[0], parts[-1]


def _with_inferred_email(contact: ContactInfo, company: CompanyInfo) -> ContactInfo:
    if contact.email or not company.email_pattern or not company.email_domain:
        return contact
    parts = _name_parts(contact.name)
    if not parts:
        return contact
    inferred = generate_email_from_pattern(parts[0], parts[1], company.email_domain, company.email_pattern)
    if not inferred:
        return contact
    return contact.model_copy(
        update={
            "email": inferred,
            "email_type": "inferred",
            "confidence": max(contact.confidence, 60),
            "confidence_reason": (
                f"Email inferred from public {company.email_domain} email pattern "
                f"'{company.email_pattern}'. Verify before outreach."
            ),
        }
    )


def _normalize_page_contact(contact: ContactInfo, company: CompanyInfo) -> ContactInfo:
    sources = contact.sources or []
    if not sources:
        source_url = company.careers_url or company.website or ""
        sources = [SourceLink(title="Visible job page contact", url=source_url)] if source_url else []
    normalized = contact.model_copy(
        update={
            "confidence": max(contact.confidence, 75),
            "confidence_reason": contact.confidence_reason
            or "Visible on the job page as a hiring team or recruiting contact. Verify before outreach.",
            "sources": sources,
        }
    )
    return _with_inferred_email(normalized, company)


def _search_leads(company: CompanyInfo) -> list[ContactInfo]:
    leads: list[ContactInfo] = []
    labels = [
        ("Recruiter search: technical recruiting", "Technical Recruiter / Talent Acquisition"),
        ("Recruiter search: university recruiting", "University Recruiter / Campus Recruiting"),
        ("Recruiter search: broader talent acquisition", "Talent Acquisition / Recruiting"),
    ]
    for (name, title), source in zip(labels, company.recruiter_search_urls, strict=False):
        leads.append(
            ContactInfo(
                name=f"{name} at {company.name}",
                title=title,
                profile_url=source.url,
                email=None,
                email_type="search_link",
                confidence=25,
                confidence_reason="Search lead only. Open the public search result and verify the person before outreach.",
                sources=[source],
            )
        )
    return leads


async def discover_contacts(company: CompanyInfo, page_contacts: list[ContactInfo] | None = None) -> list[ContactInfo]:
    contacts: list[ContactInfo] = []
    seen: set[str] = set()

    for contact in page_contacts or []:
        key = contact.name.lower()
        if key in seen:
            continue
        contacts.append(_normalize_page_contact(contact, company))
        seen.add(key)

    contacts.extend(_search_leads(company))
    return contacts
