import asyncio
import hashlib
import re

import httpx

from app.schemas.company import CompanyInfo, SourceLink
from app.schemas.contacts import ContactInfo
from app.services.email_patterns import extract_public_emails, generate_email_from_pattern
from app.services.public_search import PublicSearchResult, public_search_url, search_public_web


RECRUITING_TITLES = (
    "technical recruiter",
    "engineering recruiter",
    "talent acquisition",
    "university recruiter",
    "campus recruiter",
    "hiring manager",
    "engineering manager",
)
BAD_NAME_WORDS = {
    "linkedin",
    "profiles",
    "people",
    "jobs",
    "recruiter",
    "recruiters",
    "talent",
    "acquisition",
}


def _name_parts(name: str) -> tuple[str, str] | None:
    parts = [part.strip(" ,.") for part in name.split() if part.strip(" ,.")]
    if len(parts) < 2:
        return None
    return parts[0], parts[-1]


def _contact_id(name: str, profile_url: str | None) -> str:
    value = f"{name.lower()}|{profile_url or ''}"
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def _looks_like_person_name(value: str) -> bool:
    cleaned = re.sub(r"\s+", " ", value.strip(" .,"))
    parts = cleaned.split()
    if not 2 <= len(parts) <= 4:
        return False
    if any(part.lower() in BAD_NAME_WORDS for part in parts):
        return False
    if any(any(char.isdigit() for char in part) for part in parts):
        return False
    return all(re.match(r"^[A-Za-z][A-Za-z'.-]*$", part) for part in parts)


def _title_from_text(text: str) -> str | None:
    lower = text.lower()
    for title in RECRUITING_TITLES:
        if title in lower:
            start = max(lower.find(title) - 24, 0)
            end = min(lower.find(title) + len(title) + 28, len(text))
            fragment = text[start:end].strip(" -|,.;")
            return fragment[:90] or title.title()
    return None


def _public_email_for_name(result: PublicSearchResult, name: str, domain: str | None) -> str | None:
    if not domain:
        return None
    parts = _name_parts(name)
    if not parts:
        return None
    first, last = parts
    emails = extract_public_emails(f"{result.title} {result.snippet}", domain)
    for email in emails:
        for pattern in ("first.last", "first_last", "first-last", "firstlast", "first_initial_last", "first"):
            if email == generate_email_from_pattern(first, last, domain, pattern):
                return email
    return None


def _with_exact_email_search(contact: ContactInfo, company: CompanyInfo) -> ContactInfo:
    if contact.email or not company.email_domain or not _looks_like_person_name(contact.name):
        return contact
    source = SourceLink(
        title="Exact recruiter email search",
        url=public_search_url(f'"{contact.name}" "@{company.email_domain}"'),
    )
    if any(existing.url == source.url for existing in contact.sources):
        return contact
    return contact.model_copy(update={"sources": [*contact.sources, source]})


def _contact_from_search_result(result: PublicSearchResult, company: CompanyInfo) -> ContactInfo | None:
    text = f"{result.title} {result.snippet}"
    lower = text.lower()
    if not any(title in lower for title in RECRUITING_TITLES):
        return None
    company_name = company.name.lower()
    if company_name not in lower and company_name.replace(" ", "") not in lower.replace(" ", ""):
        return None

    clean_title = re.sub(r"\s*\|\s*LinkedIn\s*$", "", result.title, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"\s+[-–|•]\s+", clean_title) if part.strip()]
    name = next((part for part in parts[:2] if _looks_like_person_name(part)), None)
    if not name:
        match = re.search(r"([A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){1,3})", result.title)
        if match and _looks_like_person_name(match.group(1)):
            name = match.group(1)
    if not name:
        return None

    exact_email = _public_email_for_name(result, name, company.email_domain)
    source = SourceLink(title="Public recruiter search result", url=result.url)
    contact = ContactInfo(
        id=_contact_id(name, result.url),
        name=name,
        title=_title_from_text(text) or "Recruiting contact",
        profile_url=result.url,
        email=exact_email,
        email_type="public" if exact_email else None,
        confidence=95 if exact_email else 65,
        confidence_reason=(
            "Exact public email appeared with this recruiter in public search results."
            if exact_email
            else "Recruiter name and title found in public search results. Verify identity before outreach."
        ),
        sources=[source],
    )
    return contact if exact_email else _with_inferred_email(contact, company)


def _with_inferred_email(contact: ContactInfo, company: CompanyInfo) -> ContactInfo:
    if contact.email:
        return contact
    if not company.email_pattern or not company.email_domain:
        return _with_exact_email_search(contact, company)
    if company.email_pattern_confidence < 60:
        return _with_exact_email_search(contact, company)
    parts = _name_parts(contact.name)
    if not parts:
        return _with_exact_email_search(contact, company)
    inferred = generate_email_from_pattern(parts[0], parts[1], company.email_domain, company.email_pattern)
    if not inferred:
        return _with_exact_email_search(contact, company)
    return contact.model_copy(
        update={
            "email": inferred,
            "email_type": "inferred",
            "confidence": max(contact.confidence, company.email_pattern_confidence),
            "confidence_reason": (
                f"Likely email inferred from public {company.email_domain} evidence. "
                f"{company.email_pattern_reason or f'Pattern: {company.email_pattern}.'} Verify before outreach."
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
    label_by_source_title = {
        "LinkedIn company recruiter search": ("LinkedIn recruiter search at", "Recruiter / Technical Recruiter"),
        "LinkedIn company talent search": ("LinkedIn talent search at", "Talent Acquisition / People"),
        "Public recruiter search 1": ("Recruiter search: technical recruiting at", "Technical Recruiter / Talent Acquisition"),
        "Public recruiter search 2": ("Recruiter search: university recruiting at", "University Recruiter / Campus Recruiting"),
        "Public recruiter search 3": ("Recruiter search: broader talent acquisition at", "Talent Acquisition / Recruiting"),
    }
    for source in company.recruiter_search_urls:
        prefix, title = label_by_source_title.get(
            source.title,
            ("Recruiter search at", "Recruiting contact"),
        )
        leads.append(
            ContactInfo(
                name=f"{prefix} {company.name}",
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


async def _search_public_recruiters(company: CompanyInfo) -> list[ContactInfo]:
    queries = [
        f'site:linkedin.com/in "technical recruiter" "{company.name}"',
        f'site:linkedin.com/in "engineering recruiter" "{company.name}"',
        f'site:linkedin.com/in "talent acquisition" "{company.name}"',
        f'site:linkedin.com/in "university recruiter" "{company.name}"',
    ]
    async with httpx.AsyncClient(
        timeout=8,
        follow_redirects=True,
        headers={"User-Agent": "ApplyIntel local research bot"},
    ) as client:
        result_sets = await asyncio.gather(
            *(search_public_web(query, max_results=4, client=client) for query in queries),
            return_exceptions=True,
        )

    contacts: list[ContactInfo] = []
    seen: set[str] = set()
    for result_set in result_sets:
        if isinstance(result_set, Exception):
            continue
        for result in result_set:
            contact = _contact_from_search_result(result, company)
            if not contact:
                continue
            key = contact.name.lower()
            if key in seen:
                continue
            contacts.append(contact)
            seen.add(key)
    return contacts


async def discover_contacts(company: CompanyInfo, page_contacts: list[ContactInfo] | None = None) -> list[ContactInfo]:
    contacts: list[ContactInfo] = []
    seen: set[str] = set()

    for contact in page_contacts or []:
        key = contact.name.lower()
        if key in seen:
            continue
        contacts.append(_normalize_page_contact(contact, company))
        seen.add(key)

    for contact in await _search_public_recruiters(company):
        key = contact.name.lower()
        if key in seen:
            continue
        contacts.append(contact)
        seen.add(key)

    if not contacts:
        contacts.extend(_search_leads(company))
    else:
        contacts.extend(_search_leads(company)[:1])
    return contacts
