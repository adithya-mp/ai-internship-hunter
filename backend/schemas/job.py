"""
Job Schemas
Pydantic models for job-related API requests and responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class JobResponse(BaseModel):
    """Schema for job listing response."""
    id: uuid.UUID
    title: str
    company: str
    description: str
    skills_required: Optional[List[str]] = []
    location: Optional[str] = None
    apply_url: Optional[str] = None
    source: str
    job_type: Optional[str] = None
    stipend: Optional[str] = None
    duration: Optional[str] = None
    scraped_at: datetime

    class Config:
        from_attributes = True


class JobMatchResponse(BaseModel):
    """Schema for AI-matched job with score."""
    job: JobResponse
    match_score: float  # 0-100
    match_reason: str


class JobFilterParams(BaseModel):
    """Schema for job search filters."""
    query: Optional[str] = None
    location: Optional[str] = None
    company: Optional[str] = None
    skills: Optional[List[str]] = None
    source: Optional[str] = None
    page: int = 1
    per_page: int = 20


class SaveJobRequest(BaseModel):
    """Schema for saving a job."""
    job_id: uuid.UUID


class ApplicationCreate(BaseModel):
    """Schema for creating an application."""
    job_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    """Schema for updating application status."""
    status: str  # applied, in_review, interview, offer, rejected
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Schema for application response."""
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    status: str
    notes: Optional[str] = None
    applied_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None

    class Config:
        from_attributes = True
