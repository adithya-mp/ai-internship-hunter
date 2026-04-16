"""
Skill Model
Tracks user skills, certifications, and proficiency levels.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, default=50)  # 0-100 scale
    source: Mapped[str] = mapped_column(String(50), default="manual")  # manual, parsed, ai
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)  # programming, design, etc.

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="skills")
