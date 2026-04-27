"""
Resume Schemas
Pydantic models for resume and cover letter generation.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ResumeGenerateRequest(BaseModel):
    """Schema for generating a tailored resume."""
    job_id: str
    custom_instructions: Optional[str] = None


class ResumeContent(BaseModel):
    """Structured resume content."""
    summary: str
    experience: List[dict]
    education: List[dict]
    skills: List[str]
    projects: Optional[List[dict]] = []
    certifications: Optional[List[str]] = []
    achievements: Optional[List[str]] = []


class ResumeResponse(BaseModel):
    """Schema for resume response."""
    id: str
    user_id: str
    target_job_id: Optional[str] = None
    content: dict
    pdf_path: Optional[str] = None
    doc_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class CoverLetterRequest(BaseModel):
    """Schema for generating a cover letter."""
    job_id: str
    custom_instructions: Optional[str] = None


class CoverLetterResponse(BaseModel):
    """Schema for cover letter response."""
    id: str
    content: str
    job_title: str
    company: str
    pdf_path: Optional[str] = None
    created_at: datetime
