from app.services.company_research import _linkedin_company_url, _parse_h1b_summary, _recruiter_search_urls


def test_parse_h1b_summary() -> None:
    summary = _parse_h1b_summary("37 records was found, Median Salary is $135000.")

    assert summary is not None
    assert "37 LCA records" in summary
    assert "not a guarantee" in summary


def test_linkedin_company_url_is_normalized_from_public_page_html() -> None:
    html = '<a href="https://www.linkedin.com/company/loop-payments/?trk=public_jobs">LinkedIn</a>'

    assert _linkedin_company_url([html]) == "https://www.linkedin.com/company/loop-payments/"


def test_recruiter_search_urls_prefer_linkedin_company_people_search() -> None:
    urls = _recruiter_search_urls("Loop", "https://www.linkedin.com/company/loop-payments/")

    assert urls[0].title == "LinkedIn company recruiter search"
    assert urls[0].url == "https://www.linkedin.com/company/loop-payments/people/?keywords=recruiter"
    assert urls[1].title == "LinkedIn company talent search"
    assert urls[1].url == "https://www.linkedin.com/company/loop-payments/people/?keywords=talent%20acquisition"
