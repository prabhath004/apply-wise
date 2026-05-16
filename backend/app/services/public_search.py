from dataclasses import dataclass
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx
from bs4 import BeautifulSoup


SEARCH_TIMEOUT_SECONDS = 8
SEARCH_USER_AGENT = "Mozilla/5.0 ApplyIntel/0.1 local research"


@dataclass(frozen=True)
class PublicSearchResult:
    title: str
    url: str
    snippet: str


def public_search_url(query: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(query)}"


def _duckduckgo_html_url(query: str) -> str:
    return f"https://duckduckgo.com/html/?q={quote_plus(query)}"


def _clean_url(url: str) -> str:
    if url.startswith("//"):
        url = f"https:{url}"
    if url.startswith("/l/"):
        url = f"https://duckduckgo.com{url}"
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        uddg = parse_qs(parsed.query).get("uddg", [None])[0]
        if uddg:
            return unquote(uddg)
    return url


def _clean_text(value: str) -> str:
    return " ".join(value.split())


def parse_public_search_results(html: str, max_results: int = 5) -> list[PublicSearchResult]:
    soup = BeautifulSoup(html, "html.parser")
    results: list[PublicSearchResult] = []
    seen_urls: set[str] = set()

    for block in soup.select(".result"):
        anchor = block.select_one("a.result__a") or block.find("a", href=True)
        if not anchor:
            continue
        title = _clean_text(anchor.get_text(" "))
        url = _clean_url(str(anchor.get("href", "")))
        if not title or not url or url in seen_urls:
            continue
        snippet_node = block.select_one(".result__snippet") or block.select_one(".result__body")
        snippet = _clean_text(snippet_node.get_text(" ")) if snippet_node else ""
        results.append(PublicSearchResult(title=title, url=url, snippet=snippet))
        seen_urls.add(url)
        if len(results) >= max_results:
            return results

    for block in soup.select("div.g"):
        anchor = block.find("a", href=True)
        title_node = block.find("h3")
        if not anchor or not title_node:
            continue
        title = _clean_text(title_node.get_text(" "))
        url = _clean_url(str(anchor.get("href", "")))
        if not title or not url or url in seen_urls:
            continue
        snippet_node = block.select_one(".VwiC3b, .IsZvec")
        snippet = _clean_text(snippet_node.get_text(" ")) if snippet_node else ""
        results.append(PublicSearchResult(title=title, url=url, snippet=snippet))
        seen_urls.add(url)
        if len(results) >= max_results:
            break

    return results


async def search_public_web(
    query: str,
    max_results: int = 5,
    client: httpx.AsyncClient | None = None,
) -> list[PublicSearchResult]:
    async def _run(active_client: httpx.AsyncClient) -> list[PublicSearchResult]:
        try:
            response = await active_client.get(_duckduckgo_html_url(query))
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        return parse_public_search_results(response.text, max_results=max_results)

    if client:
        return await _run(client)

    async with httpx.AsyncClient(
        timeout=SEARCH_TIMEOUT_SECONDS,
        follow_redirects=True,
        headers={"User-Agent": SEARCH_USER_AGENT},
    ) as owned_client:
        return await _run(owned_client)
