import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
    )
    target_job_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("jobs.id"), nullable=True
    )

    # Resume content as structured JSON
    content: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Cover letter content (if generated alongside)
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Path to generated PDF file
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_letter_pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Type: 'resume' or 'cover_letter'
    doc_type: Mapped[str] = mapped_column(String(20), default="resume")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="resumes")
    target_job = relationship("Job")
    applications = relationship("Application", back_populates="resume")
