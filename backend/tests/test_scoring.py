from app.schemas.job import ParsedJob
from app.services.resume_parser import parse_resume_text
from app.services.scoring import recommendation_for_score, score_fit


def test_fit_score_thresholds() -> None:
    assert recommendation_for_score(90) == "Strong Apply"
    assert recommendation_for_score(75) == "Apply"
    assert recommendation_for_score(60) == "Maybe"
    assert recommendation_for_score(40) == "Low Fit"


def test_scoring_matches_and_missing_skills() -> None:
    resume = parse_resume_text("Jane Doe\nUniversity\nSkills: Python, FastAPI, AWS")
    job = ParsedJob(required_skills=["Python", "React", "AWS"], seniority="entry_level", domain="software")

    score = score_fit(resume, job)

    assert "Python" in score.matching_skills
    assert "AWS" in score.matching_skills
    assert "React" in score.missing_skills
    assert 0 <= score.overall <= 100
