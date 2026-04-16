"""
User Model
Stores user accounts, profiles, and authentication data.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Profile data stored as JSON for flexibility
    # Contains: education, experience, projects, links, phone, etc.
    profile_data: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    # Embedding vector stored as JSON array (list of floats)
    embedding: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
