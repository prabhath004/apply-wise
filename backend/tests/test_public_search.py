from app.services.public_search import parse_public_search_results


def test_parse_duckduckgo_search_results() -> None:
    html = """
    <div class="result">
      <a class="result__a" href="/l/?uddg=https%3A%2F%2Fwww.linkedin.com%2Fin%2Fsarah-kim">
        Sarah Kim - Senior Technical Recruiter - Stripe | LinkedIn
      </a>
      <a class="result__snippet">Sarah Kim recruits software engineers at Stripe.</a>
    </div>
    """

    results = parse_public_search_results(html)

    assert len(results) == 1
    assert results[0].title == "Sarah Kim - Senior Technical Recruiter - Stripe | LinkedIn"
    assert results[0].url == "https://www.linkedin.com/in/sarah-kim"
    assert "software engineers" in results[0].snippet
