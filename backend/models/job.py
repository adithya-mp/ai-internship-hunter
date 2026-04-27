import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skills_required: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    apply_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="mock")
    job_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # internship, full-time
    stipend: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Embedding vector for AI matching
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    applications = relationship("Application", back_populates="job")
    saved_by = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("jobs.id"), nullable=False
    )
    saved_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")
