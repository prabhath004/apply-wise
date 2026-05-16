import asyncio

from app.schemas.job import JobInput, ParsedJob
from app.services.resume_parser import parse_resume_text
from app.services.scoring import recommendation_for_score, score_fit, score_fit_with_openai


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


def test_openai_scoring_validates_model_output() -> None:
    class FakeLLM:
        async def json_completion(self, system_prompt: str, user_prompt: str) -> dict:
            assert "holistic fit" in system_prompt
            return {
                "overall": 88,
                "recommendation": "Apply",
                "breakdown": {
                    "skills": 90,
                    "experience": 85,
                    "seniority": 90,
                    "domain": 85,
                    "education": 90,
                },
                "matching_skills": ["Python", "FastAPI"],
                "missing_skills": ["Kubernetes"],
                "strengths": ["Resume shows backend API experience relevant to the role."],
                "risks": ["Kubernetes is mentioned in the job but not clearly in the resume."],
            }

    resume = parse_resume_text("Jane Doe\nUniversity\nSkills: Python, FastAPI")
    parsed_job = ParsedJob(required_skills=["Python", "FastAPI", "Kubernetes"], seniority="entry_level", domain="software")
    local_score = score_fit(resume, parsed_job)

    score = asyncio.run(
        score_fit_with_openai(
            llm_client=FakeLLM(),
            resume_text="Jane Doe\nBuilt APIs with Python and FastAPI.",
            parsed_resume=resume,
            job_input=JobInput(
                source="manual",
                job_title="Backend Engineer",
                company_name="Example",
                job_description="Build APIs with Python and FastAPI.",
            ),
            parsed_job=parsed_job,
            local_score=local_score,
        )
    )

    assert score.overall == 88
    assert score.recommendation == "Strong Apply"
