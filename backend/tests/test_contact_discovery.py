import asyncio

from app.schemas.company import CompanyInfo, SourceLink
from app.schemas.contacts import ContactInfo
from app.services.public_search import PublicSearchResult
from app.services.contact_discovery import discover_contacts


def test_discover_contacts_includes_visible_job_page_contacts_and_search_leads(monkeypatch) -> None:
    async def fake_search(*args, **kwargs):
        return []

    monkeypatch.setattr("app.services.contact_discovery.search_public_web", fake_search)

    contacts = asyncio.run(
        discover_contacts(
            CompanyInfo(
                name="Example",
                recruiter_search_urls=[SourceLink(title="Search", url="https://www.google.com/search?q=example")],
            ),
            [
                ContactInfo(
                    name="Jane Recruiter",
                    title="Technical Recruiter",
                    confidence=80,
                    sources=[SourceLink(title="LinkedIn job page", url="https://linkedin.com/jobs/view/1")],
                )
            ],
        )
    )

    assert contacts[0].name == "Jane Recruiter"
    assert contacts[0].confidence >= 75
    assert any(contact.email_type == "search_link" for contact in contacts)


def test_discover_contacts_infers_recruiter_email_from_pattern(monkeypatch) -> None:
    async def fake_search(*args, **kwargs):
        return [
            PublicSearchResult(
                title="Sarah Kim - Senior Technical Recruiter - Stripe | LinkedIn",
                url="https://www.linkedin.com/in/sarah-kim",
                snippet="Sarah Kim hires software engineers at Stripe.",
            )
        ]

    monkeypatch.setattr("app.services.contact_discovery.search_public_web", fake_search)

    contacts = asyncio.run(
        discover_contacts(
            CompanyInfo(
                name="Stripe",
                email_domain="stripe.com",
                email_pattern="first.last",
                email_pattern_confidence=85,
                email_pattern_reason="Company uses first.last format based on 3 public employee emails.",
                public_emails=["alex.johnson@stripe.com", "maria.lee@stripe.com", "john.doe@stripe.com"],
            )
        )
    )

    sarah = next(contact for contact in contacts if contact.name == "Sarah Kim")
    assert sarah.email == "sarah.kim@stripe.com"
    assert sarah.email_type == "inferred"
    assert sarah.confidence >= 85
    assert "3 public employee emails" in (sarah.confidence_reason or "")


def test_discover_contacts_does_not_show_weak_inferred_email(monkeypatch) -> None:
    async def fake_search(*args, **kwargs):
        return [
            PublicSearchResult(
                title="Sarah Kim - Senior Technical Recruiter - Stripe | LinkedIn",
                url="https://www.linkedin.com/in/sarah-kim",
                snippet="Sarah Kim hires software engineers at Stripe.",
            )
        ]

    monkeypatch.setattr("app.services.contact_discovery.search_public_web", fake_search)

    contacts = asyncio.run(
        discover_contacts(
            CompanyInfo(
                name="Stripe",
                email_domain="stripe.com",
                email_pattern="first.last",
                email_pattern_confidence=55,
                email_pattern_reason="Company uses first.last format based on 1 public employee email.",
            )
        )
    )

    sarah = next(contact for contact in contacts if contact.name == "Sarah Kim")
    assert sarah.email is None
    assert any(source.title == "Exact recruiter email search" for source in sarah.sources)
