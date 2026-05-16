import asyncio

from app.schemas.company import CompanyInfo, SourceLink
from app.schemas.contacts import ContactInfo
from app.services.contact_discovery import discover_contacts


def test_discover_contacts_includes_visible_job_page_contacts_and_search_leads() -> None:
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
