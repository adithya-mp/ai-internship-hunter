"""
Application Model
Tracks user's job applications and their statuses.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id"), nullable=False
    )
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("resumes.id"), nullable=True
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
