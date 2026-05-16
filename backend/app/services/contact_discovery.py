from app.schemas.company import CompanyInfo
from app.schemas.contacts import ContactInfo


RECRUITING_TITLES = (
    "technical recruiter",
    "engineering recruiter",
    "talent acquisition",
    "university recruiter",
    "hiring manager",
    "engineering manager",
)


async def discover_contacts(company: CompanyInfo) -> list[ContactInfo]:
    if not company.sources:
        return []
    return []
