from app.services.job_parser import parse_job


def test_job_parser_basic_cases() -> None:
    parsed = parse_job(
        "Software Engineer I",
        """
        Build REST APIs with Python and React.
        0+ years of experience.
        We are unable to sponsor visas for this role.
        """
    )

    assert parsed.role_category == "software_engineering"
    assert parsed.seniority == "entry_level"
    assert "Python" in parsed.required_skills
    assert "React" in parsed.required_skills
    assert parsed.years_experience_min == 0
    assert parsed.visa_signals.mentions_no_sponsorship is True
