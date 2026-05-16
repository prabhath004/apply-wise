from app.services.email_patterns import (
    dominant_pattern,
    dominant_pattern_evidence,
    extract_public_emails,
    generate_email_from_pattern,
    infer_pattern,
)


def test_email_pattern_inference() -> None:
    assert infer_pattern("jane.doe@example.com", "Jane", "Doe") == "first.last"
    assert infer_pattern("jdoe@example.com", "Jane", "Doe") == "first_initial_last"
    assert generate_email_from_pattern("Jane", "Doe", "example.com", "first.last") == "jane.doe@example.com"


def test_public_email_extraction_and_dominant_pattern() -> None:
    emails = extract_public_emails("Email jane.doe@example.com and sam.lee@example.com.", "example.com")
    pattern, confidence = dominant_pattern(emails)

    assert emails == ["jane.doe@example.com", "sam.lee@example.com"]
    assert pattern == "first.last"
    assert confidence == 75


def test_dominant_pattern_evidence_ignores_generic_emails() -> None:
    emails = extract_public_emails(
        "Email info@example.com, jane.doe@example.com, sam.lee@example.com, alex.kim@example.com.",
        "example.com",
    )
    evidence = dominant_pattern_evidence(emails)

    assert "info@example.com" not in emails
    assert evidence.pattern == "first.last"
    assert evidence.confidence == 85
    assert evidence.count == 3
