import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id"), nullable=False
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
