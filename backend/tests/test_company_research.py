from app.services.company_research import _parse_h1b_summary


def test_parse_h1b_summary() -> None:
    summary = _parse_h1b_summary("37 records was found, Median Salary is $135000.")

    assert summary is not None
    assert "37 LCA records" in summary
    assert "not a guarantee" in summary
