from app.services.resume_parser import parse_resume_text
from app.utils.text import normalize_multiline_text


def test_resume_text_normalization() -> None:
    assert normalize_multiline_text("A  B\n\n C") == "A B\nC"


def test_resume_parser_extracts_basic_profile() -> None:
    parsed = parse_resume_text(
        """
        Jane Doe
        jane@example.com
        University of Example, BS Computer Science
        Skills: Python, React, AWS, PostgreSQL
        """
    )

    assert parsed.name == "Jane Doe"
    assert parsed.email == "jane@example.com"
    assert "Python" in parsed.skills.languages
    assert "React" in parsed.skills.frameworks
    assert parsed.education
