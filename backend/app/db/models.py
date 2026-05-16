from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    created_at: Mapped[str] = mapped_column(default=utc_now)
    updated_at: Mapped[str] = mapped_column(default=utc_now)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    file_name: Mapped[str]
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=utc_now)
    updated_at: Mapped[str] = mapped_column(default=utc_now)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    source: Mapped[str]
    job_title: Mapped[str]
    company_name: Mapped[str]
    location: Mapped[str | None]
    job_url: Mapped[str | None]
    job_description: Mapped[str] = mapped_column(Text)
    parsed_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=utc_now)
    updated_at: Mapped[str] = mapped_column(default=utc_now)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    resume_id: Mapped[str] = mapped_column(ForeignKey("resumes.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id"), index=True)
    fit_score_json: Mapped[str] = mapped_column(Text)
    company_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=utc_now)
    updated_at: Mapped[str] = mapped_column(default=utc_now)

    job: Mapped[Job] = relationship()
    contacts: Mapped[list["Contact"]] = relationship(cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), index=True)
    name: Mapped[str]
    title: Mapped[str | None]
    profile_url: Mapped[str | None]
    email: Mapped[str | None]
    email_type: Mapped[str | None]
    confidence: Mapped[int]
    confidence_reason: Mapped[str | None]
    sources_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=utc_now)
    updated_at: Mapped[str] = mapped_column(default=utc_now)


class OutreachMessage(Base):
    __tablename__ = "outreach_messages"

    id: Mapped[str] = mapped_column(primary_key=True, default=new_id)
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), index=True)
    contact_id: Mapped[str | None] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    channel: Mapped[str]
    tone: Mapped[str]
    subject: Mapped[str | None]
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(default=utc_now)
