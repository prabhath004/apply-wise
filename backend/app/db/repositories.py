import json
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import Analysis, Contact, Job, OutreachMessage, Resume, User


LOCAL_USER_ID = "local-user"


def ensure_local_user(db: Session) -> User:
    user = db.get(User, LOCAL_USER_ID)
    if user:
        return user
    user = User(id=LOCAL_USER_ID)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True)


def json_load(value: str | None, fallback: Any = None) -> Any:
    if value is None:
        return fallback
    return json.loads(value)


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, file_name: str, raw_text: str, parsed: dict[str, Any]) -> Resume:
        user = ensure_local_user(self.db)
        resume = Resume(
            user_id=user.id,
            file_name=file_name,
            raw_text=raw_text,
            parsed_json=json_dump(parsed),
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get(self, resume_id: str) -> Resume | None:
        return self.db.get(Resume, resume_id)


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job_data: dict[str, Any], parsed: dict[str, Any]) -> Job:
        user = ensure_local_user(self.db)
        job = Job(
            user_id=user.id,
            source=job_data["source"],
            job_title=job_data["job_title"],
            company_name=job_data["company_name"],
            location=job_data.get("location"),
            job_url=job_data.get("job_url"),
            job_description=job_data["job_description"],
            parsed_json=json_dump(parsed),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def create_analysis(
        self,
        resume_id: str,
        job_id: str,
        fit_score: dict[str, Any],
        company: dict[str, Any],
    ) -> Analysis:
        user = ensure_local_user(self.db)
        analysis = Analysis(
            user_id=user.id,
            resume_id=resume_id,
            job_id=job_id,
            fit_score_json=json_dump(fit_score),
            company_json=json_dump(company),
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def add_contacts(self, analysis_id: str, contacts: list[dict[str, Any]]) -> list[Contact]:
        rows: list[Contact] = []
        for contact_data in contacts:
            contact = Contact(
                analysis_id=analysis_id,
                name=contact_data["name"],
                title=contact_data.get("title"),
                profile_url=contact_data.get("profile_url"),
                email=contact_data.get("email"),
                email_type=contact_data.get("email_type"),
                confidence=contact_data["confidence"],
                confidence_reason=contact_data.get("confidence_reason"),
                sources_json=json_dump(contact_data.get("sources", [])),
            )
            self.db.add(contact)
            rows.append(contact)
        self.db.commit()
        for row in rows:
            self.db.refresh(row)
        return rows

    def get_analysis(self, analysis_id: str) -> Analysis | None:
        return self.db.get(Analysis, analysis_id)

    def get_contact(self, contact_id: str) -> Contact | None:
        return self.db.get(Contact, contact_id)

    def create_outreach(
        self,
        analysis_id: str,
        contact_id: str | None,
        channel: str,
        tone: str,
        subject: str | None,
        body: str,
    ) -> OutreachMessage:
        message = OutreachMessage(
            analysis_id=analysis_id,
            contact_id=contact_id,
            channel=channel,
            tone=tone,
            subject=subject,
            body=body,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
