from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.repositories import ResumeRepository
from app.db.session import get_db
from app.schemas.resume import ResumeUploadResponse
from app.services.resume_parser import parse_resume_text, read_resume_upload


router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ResumeUploadResponse:
    file_name = file.filename or "resume"
    if not file_name.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "unsupported_resume_type", "message": "Upload a PDF or TXT resume."},
        )

    raw_text = await read_resume_upload(file)
    if not raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "empty_resume", "message": "Could not extract text from the uploaded resume."},
        )

    parsed = parse_resume_text(raw_text)
    row = ResumeRepository(db).create(file_name=file_name, raw_text=raw_text, parsed=parsed.model_dump())
    return ResumeUploadResponse(resume_id=row.id, name=parsed.name, parsed_profile=parsed)
