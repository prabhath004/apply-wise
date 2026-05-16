from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AnalysisRepository, ResumeRepository, json_load
from app.db.session import get_db
from app.schemas.analysis import AnalyzeJobRequest, AnalyzeJobResponse
from app.schemas.contacts import ContactInfo
from app.schemas.resume import ParsedResumeProfile
from app.services.company_research import research_company
from app.services.contact_discovery import discover_contacts
from app.services.job_parser import parse_job
from app.services.llm_client import LLMClient
from app.services.scoring import score_fit, score_fit_with_openai


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/job", response_model=AnalyzeJobResponse)
async def analyze_job(
    payload: AnalyzeJobRequest,
    db: Session = Depends(get_db),
    openai_api_key: Annotated[str | None, Header(alias="X-OpenAI-API-Key")] = None,
) -> AnalyzeJobResponse:
    resume = ResumeRepository(db).get(payload.resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "resume_not_found", "message": "Upload a resume before analyzing a job."},
        )

    parsed_resume = ParsedResumeProfile.model_validate(json_load(resume.parsed_json, {}))
    parsed_job = parse_job(payload.job.job_title, payload.job.job_description)
    local_score = score_fit(parsed_resume, parsed_job)
    fit_score = await score_fit_with_openai(
        llm_client=LLMClient(openai_api_key),
        resume_text=resume.raw_text,
        parsed_resume=parsed_resume,
        job_input=payload.job,
        parsed_job=parsed_job,
        local_score=local_score,
    )
    company = await research_company(payload.job.company_name, payload.job.job_url)
    contacts = await discover_contacts(company, payload.job.page_contacts)

    repo = AnalysisRepository(db)
    job = repo.create_job(payload.job.model_dump(), parsed_job.model_dump())
    analysis = repo.create_analysis(
        resume_id=resume.id,
        job_id=job.id,
        fit_score=fit_score.model_dump(),
        company=company.model_dump(),
    )
    contact_rows = repo.add_contacts(analysis.id, [contact.model_dump() for contact in contacts])
    contact_models = [
        ContactInfo(
            id=row.id,
            name=row.name,
            title=row.title,
            profile_url=row.profile_url,
            email=row.email,
            email_type=row.email_type,
            confidence=row.confidence,
            confidence_reason=row.confidence_reason,
            sources=json_load(row.sources_json, []),
        )
        for row in contact_rows
    ]

    return AnalyzeJobResponse(
        analysis_id=analysis.id,
        job_id=job.id,
        fit_score=fit_score,
        company=company,
        contacts=contact_models,
    )
