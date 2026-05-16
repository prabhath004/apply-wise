import asyncio

from app.schemas.analysis import FitScore, ScoreBreakdown
from app.schemas.company import CompanyInfo
from app.services.outreach import generate_openai_outreach


def test_openai_outreach_validates_model_output() -> None:
    class FakeLLM:
        async def json_completion(self, system_prompt: str, user_prompt: str) -> dict:
            assert "No emojis" in system_prompt
            return {
                "subject": "Backend Engineer role at Example",
                "body": "Hi there,\n\nI am interested in the Backend Engineer role at Example. My background includes Python API work and React projects, and the role appears aligned with that experience.\n\nBest,\nJane",
            }

    fit_score = FitScore(
        overall=82,
        recommendation="Apply",
        breakdown=ScoreBreakdown(skills=85, experience=80, seniority=85, domain=75, education=80),
        matching_skills=["Python", "React"],
        missing_skills=["Kubernetes"],
        strengths=["Resume shows relevant API work."],
        risks=["Kubernetes is not clear on the resume."],
    )

    subject, body = asyncio.run(
        generate_openai_outreach(
            llm_client=FakeLLM(),
            resume_text="Jane Doe\nBuilt APIs with Python.",
            job_title="Backend Engineer",
            company_name="Example",
            job_description="Build backend APIs.",
            fit_score=fit_score,
            company=CompanyInfo(name="Example"),
            contact=None,
            tone="concise",
            channel="email",
        )
    )

    assert subject == "Backend Engineer role at Example"
    assert "Backend Engineer" in body
