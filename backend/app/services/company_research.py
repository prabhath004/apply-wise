from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.schemas.company import CompanyInfo, SourceLink
from app.utils.urls import domain_from_url


CAREERS_TERMS = ("careers", "jobs", "join us")
ABOUT_TERMS = ("about", "company")


def _visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    return " ".join(soup.get_text(" ").split())


def _link_for_terms(base_url: str, html: str, terms: tuple[str, ...]) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        label = " ".join(anchor.get_text(" ").split()).lower()
        href = anchor["href"]
        if any(term in label or term in href.lower() for term in terms):
            return urljoin(base_url, href)
    return None


def _summary_from_text(text: str) -> str | None:
    sentences = [part.strip() for part in text.split(".") if 60 <= len(part.strip()) <= 240]
    if not sentences:
        return None
    return f"{sentences[0]}."


async def research_company(company_name: str, job_url: str | None = None) -> CompanyInfo:
    domain = domain_from_url(job_url)
    if not domain or "linkedin.com" in domain:
        return CompanyInfo(
            name=company_name,
            summary=None,
            notes=["No company website was available from the job URL. Company research is partial."],
            sources=[],
        )

    website = f"https://{domain}"
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
            response = await client.get(website)
            response.raise_for_status()
    except httpx.HTTPError:
        return CompanyInfo(
            name=company_name,
            website=website,
            notes=["Could not fetch the company website from the available URL."],
            sources=[],
        )

    text = _visible_text(response.text)
    careers_url = _link_for_terms(str(response.url), response.text, CAREERS_TERMS)
    about_url = _link_for_terms(str(response.url), response.text, ABOUT_TERMS)
    sources = [SourceLink(title="Company website", url=str(response.url))]
    if about_url:
        sources.append(SourceLink(title="About page", url=about_url))
    if careers_url:
        sources.append(SourceLink(title="Careers page", url=careers_url))

    return CompanyInfo(
        name=company_name,
        summary=_summary_from_text(text),
        website=str(response.url),
        careers_url=careers_url,
        sources=sources,
    )
