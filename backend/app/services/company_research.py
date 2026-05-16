import asyncio
import re
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from app.schemas.company import CompanyInfo, SourceLink
from app.services.email_patterns import dominant_pattern_evidence, extract_public_emails
from app.services.public_search import public_search_url, search_public_web
from app.utils.urls import domain_from_url


CAREERS_TERMS = ("careers", "jobs", "join us", "open roles")
ABOUT_TERMS = ("about", "company", "what we do")
CONTACT_TERMS = ("contact", "team", "leadership", "people")
COMMON_TLDS = ("com", "io", "ai", "co", "net", "org")
DROP_WORDS = {
    "inc",
    "incorporated",
    "llc",
    "ltd",
    "limited",
    "corp",
    "corporation",
    "company",
    "co",
    "group",
}


def _visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for element in soup(["script", "style", "noscript"]):
        element.decompose()
    return " ".join(soup.get_text(" ").split())


def _meta_summary(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for attrs in (
        {"name": "description"},
        {"property": "og:description"},
        {"name": "twitter:description"},
    ):
        tag = soup.find("meta", attrs=attrs)
        content = tag.get("content") if tag else None
        if isinstance(content, str) and len(content.strip()) > 40:
            return " ".join(content.split())
    return None


def _link_for_terms(base_url: str, html: str, terms: tuple[str, ...]) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for anchor in soup.find_all("a", href=True):
        label = " ".join(anchor.get_text(" ").split()).lower()
        href = anchor["href"]
        if any(term in label or term in href.lower() for term in terms):
            return urljoin(base_url, href)
    return None


def _summary_from_text(text: str) -> str | None:
    sentences = [part.strip() for part in text.split(".") if 60 <= len(part.strip()) <= 260]
    if not sentences:
        return None
    return f"{sentences[0]}."


def _company_slug(company_name: str) -> str:
    words = re.findall(r"[a-z0-9]+", company_name.lower())
    kept = [word for word in words if word not in DROP_WORDS]
    return "".join(kept)


def _candidate_websites(company_name: str, job_url: str | None) -> list[str]:
    domain = domain_from_url(job_url)
    if domain and "linkedin.com" not in domain:
        return [f"https://{domain}"]

    slug = _company_slug(company_name)
    if not slug:
        return []
    return [f"https://{slug}.{tld}" for tld in COMMON_TLDS]


async def _fetch(client: httpx.AsyncClient, url: str) -> tuple[str, str] | None:
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        return None
    return str(response.url), response.text


async def _find_company_homepage(company_name: str, job_url: str | None) -> tuple[str, str] | None:
    async with httpx.AsyncClient(
        timeout=8,
        follow_redirects=True,
        headers={"User-Agent": "ApplyIntel local research bot"},
    ) as client:
        for url in _candidate_websites(company_name, job_url):
            fetched = await _fetch(client, url)
            if not fetched:
                continue
            final_url, html = fetched
            text = _visible_text(html).lower()
            slug = _company_slug(company_name)
            if slug and (slug in domain_from_url(final_url).replace(".", "") or company_name.lower().split()[0] in text[:3000]):
                return final_url, html
    return None


def _recruiter_search_urls(company_name: str) -> list[SourceLink]:
    queries = [
        f'site:linkedin.com/in "{company_name}" ("technical recruiter" OR "talent acquisition")',
        f'site:linkedin.com/in "{company_name}" ("university recruiter" OR "campus recruiter")',
        f'"{company_name}" "talent acquisition" recruiter',
    ]
    return [
        SourceLink(title=f"Public recruiter search {index}", url=public_search_url(query))
        for index, query in enumerate(queries, start=1)
    ]


def _h1b_url(company_name: str) -> str:
    return f"https://h1bdata.info/index.php?em={quote_plus(company_name)}"


def _parse_h1b_summary(html: str) -> str | None:
    text = _visible_text(html)
    match = re.search(r"(\d+)\s+records\s+was\s+found,\s+Median Salary is\s+\$?([\d,]+)", text, re.IGNORECASE)
    if match:
        records, median = match.groups()
        return f"H1BData shows {records} LCA records with a median salary of ${median}. LCA records are evidence of filings, not a guarantee that this role sponsors."
    if "0 records was found" in text.lower():
        return "H1BData shows 0 LCA records for this exact employer search. Verify spelling and related legal entities."
    return None


async def _h1b_summary(company_name: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "ApplyIntel local research bot"}) as client:
            response = await client.get(_h1b_url(company_name))
            response.raise_for_status()
    except httpx.HTTPError:
        return None
    return _parse_h1b_summary(response.text)


async def _fetch_extra_pages(home_url: str, home_html: str) -> tuple[list[SourceLink], list[str], list[str]]:
    pages: list[tuple[str, tuple[str, ...], str]] = [
        ("About page", ABOUT_TERMS, home_url),
        ("Careers page", CAREERS_TERMS, home_url),
        ("Contact or team page", CONTACT_TERMS, home_url),
    ]
    sources: list[SourceLink] = []
    texts = [_visible_text(home_html)]
    html_pages = [home_html]

    async with httpx.AsyncClient(
        timeout=8,
        follow_redirects=True,
        headers={"User-Agent": "ApplyIntel local research bot"},
    ) as client:
        for title, terms, base_url in pages:
            link = _link_for_terms(base_url, home_html, terms)
            if not link:
                continue
            fetched = await _fetch(client, link)
            if not fetched:
                continue
            final_url, html = fetched
            sources.append(SourceLink(title=title, url=final_url))
            texts.append(_visible_text(html))
            html_pages.append(html)

    return sources, texts, html_pages


def _same_domain_or_subdomain(url: str, domain: str) -> bool:
    result_domain = domain_from_url(url)
    return bool(result_domain and (result_domain == domain or result_domain.endswith(f".{domain}")))


async def _fetch_email_text(client: httpx.AsyncClient, url: str) -> str | None:
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" in content_type:
        return response.text
    if "text/plain" in content_type or "application/pdf" in content_type:
        return response.content.decode("latin-1", errors="ignore")
    return None


async def _public_email_search(company_name: str, email_domain: str) -> list[str]:
    queries = [
        f'site:{email_domain} "@{email_domain}"',
        f'filetype:pdf "@{email_domain}"',
        f'"@{email_domain}" "{company_name}"',
    ]
    emails: list[str] = []
    async with httpx.AsyncClient(
        timeout=8,
        follow_redirects=True,
        headers={"User-Agent": "ApplyIntel local research bot"},
    ) as client:
        result_sets = await asyncio.gather(
            *(search_public_web(query, max_results=5, client=client) for query in queries),
            return_exceptions=True,
        )
        results = [
            result
            for result_set in result_sets
            if not isinstance(result_set, Exception)
            for result in result_set
        ]

        for result in results:
            emails.extend(extract_public_emails(f"{result.title} {result.snippet}", email_domain))

        fetchable_urls: list[str] = []
        for result in results:
            if not _same_domain_or_subdomain(result.url, email_domain):
                continue
            if result.url in fetchable_urls:
                continue
            fetchable_urls.append(result.url)
            if len(fetchable_urls) >= 5:
                break

        page_texts = await asyncio.gather(
            *(_fetch_email_text(client, url) for url in fetchable_urls),
            return_exceptions=True,
        )
        for text in page_texts:
            if isinstance(text, str):
                emails.extend(extract_public_emails(text, email_domain))

    return sorted(set(emails))


async def research_company(company_name: str, job_url: str | None = None) -> CompanyInfo:
    h1b_data_url = _h1b_url(company_name)
    h1b_summary = await _h1b_summary(company_name)
    recruiter_search_urls = _recruiter_search_urls(company_name)
    homepage = await _find_company_homepage(company_name, job_url)

    if not homepage:
        return CompanyInfo(
            name=company_name,
            summary=None,
            h1b_data_url=h1b_data_url,
            h1b_summary=h1b_summary,
            recruiter_search_urls=recruiter_search_urls,
            notes=[
                "Could not verify the company website from the job URL or common domain guesses.",
                "Recruiter and H1B links are search leads and should be verified manually.",
            ],
            sources=[SourceLink(title="H1BData employer search", url=h1b_data_url)],
        )

    website, home_html = homepage
    extra_sources, texts, html_pages = await _fetch_extra_pages(website, home_html)
    careers_url = next((source.url for source in extra_sources if source.title == "Careers page"), None)
    summary = _meta_summary(home_html) or _summary_from_text(" ".join(texts))
    email_domain = domain_from_url(website)
    emails: list[str] = []
    for html in html_pages:
        emails.extend(extract_public_emails(html, email_domain))
    emails = sorted(set(emails))
    public_search_emails = await _public_email_search(company_name, email_domain) if email_domain else []
    emails = sorted(set([*emails, *public_search_emails]))
    pattern_evidence = dominant_pattern_evidence(emails)

    sources = [SourceLink(title="Company website", url=website), *extra_sources, SourceLink(title="H1BData employer search", url=h1b_data_url)]
    notes = ["Recruiter search links are public-search leads; verify identity before outreach."]
    if h1b_summary:
        notes.append(h1b_summary)

    return CompanyInfo(
        name=company_name,
        summary=summary,
        website=website,
        careers_url=careers_url,
        public_emails=emails[:10],
        email_pattern=pattern_evidence.pattern,
        email_domain=email_domain,
        email_pattern_confidence=pattern_evidence.confidence,
        email_pattern_reason=pattern_evidence.reason,
        h1b_data_url=h1b_data_url,
        h1b_summary=h1b_summary,
        recruiter_search_urls=recruiter_search_urls,
        notes=notes,
        sources=sources,
    )
