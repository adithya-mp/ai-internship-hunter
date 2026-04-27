import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("jobs.id"), nullable=False
    )
    resume_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("resumes.id"), nullable=True
    )

    # Status: applied, in_review, interview, offer, rejected
    status: Mapped[str] = mapped_column(String(50), default="applied")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    applied_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
