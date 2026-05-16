from fastapi.testclient import TestClient

from app.schemas.analysis import FitScore
from main import app


def test_resume_upload_and_job_analysis_smoke(monkeypatch) -> None:
    async def fake_score_fit_with_openai(**kwargs) -> FitScore:
        return kwargs["local_score"]

    monkeypatch.setattr("app.api.routes.analysis.score_fit_with_openai", fake_score_fit_with_openai)

    client = TestClient(app)
    resume_response = client.post(
        "/resumes/upload",
        files={
            "file": (
                "resume.txt",
                b"Jane Doe\njane@example.com\nUniversity\nSkills: Python, React, AWS",
                "text/plain",
            )
        },
    )

    assert resume_response.status_code == 200
    resume_id = resume_response.json()["resume_id"]

    analysis_response = client.post(
        "/analysis/job",
        json={
            "resume_id": resume_id,
            "job": {
                "source": "manual",
                "job_title": "Software Engineer I",
                "company_name": "Example Co",
                "location": "Remote",
                "job_url": "",
                "job_description": "Build Python and React APIs.",
            },
        },
    )

    assert analysis_response.status_code == 200
    assert analysis_response.json()["fit_score"]["overall"] > 0
