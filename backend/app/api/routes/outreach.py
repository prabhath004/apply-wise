from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.repositories import AnalysisRepository, ResumeRepository, json_load
from app.db.session import get_db
from app.schemas.analysis import FitScore
from app.schemas.company import CompanyInfo
from app.schemas.contacts import ContactInfo
from app.schemas.outreach import OutreachGenerateRequest, OutreachResponse
from app.services.llm_client import LLMClient
from app.services.outreach import generate_openai_outreach


router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.post("/generate", response_model=OutreachResponse)
async def generate_outreach(
    payload: OutreachGenerateRequest,
    db: Session = Depends(get_db),
    openai_api_key: Annotated[str | None, Header(alias="X-OpenAI-API-Key")] = None,
) -> OutreachResponse:
    repo = AnalysisRepository(db)
    analysis = repo.get_analysis(payload.analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "analysis_not_found", "message": "Analyze a job before generating outreach."},
        )

    contact = None
    if payload.contact_id:
        contact_row = repo.get_contact(payload.contact_id)
        if not contact_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "contact_not_found", "message": "The selected contact was not found."},
            )
        contact = ContactInfo(
            id=contact_row.id,
            name=contact_row.name,
            title=contact_row.title,
            profile_url=contact_row.profile_url,
            email=contact_row.email,
            email_type=contact_row.email_type,
            confidence=contact_row.confidence,
            confidence_reason=contact_row.confidence_reason,
            sources=json_load(contact_row.sources_json, []),
        )

    fit_score = FitScore.model_validate(json_load(analysis.fit_score_json, {}))
    company = CompanyInfo.model_validate(json_load(analysis.company_json, {}))
    job = analysis.job if hasattr(analysis, "job") else None
    job_title = job.job_title if job else "the open"
    company_name = company.name
    job_description = job.job_description if job else ""
    resume = ResumeRepository(db).get(analysis.resume_id)
    resume_text = resume.raw_text if resume else ""

    subject, body = await generate_openai_outreach(
        llm_client=LLMClient(openai_api_key),
        resume_text=resume_text,
        job_title=job_title,
        company_name=company_name,
        job_description=job_description,
        fit_score=fit_score,
        company=company,
        contact=contact,
        tone=payload.tone,
        channel=payload.channel,
    )
    row = repo.create_outreach(
        analysis_id=analysis.id,
        contact_id=payload.contact_id,
        channel=payload.channel,
        tone=payload.tone,
        subject=subject,
        body=body,
    )
    return OutreachResponse(outreach_id=row.id, subject=subject, body=body)
