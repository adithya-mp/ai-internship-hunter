"""
Skill Schemas
Pydantic models for skill tracking and analysis.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class SkillCreate(BaseModel):
    """Schema for adding a skill."""
    name: str
    proficiency: int = 50  # 0-100
    category: Optional[str] = None


class SkillResponse(BaseModel):
    """Schema for skill response."""
    id: uuid.UUID
    name: str
    proficiency: int
    source: str
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SkillGapAnalysis(BaseModel):
    """Schema for skill gap analysis result."""
    matching_skills: List[str]
    missing_skills: List[str]
    match_percentage: float
    recommendations: List[dict]  # {skill, reason, resources}


class SkillAnalyzeRequest(BaseModel):
    """Schema for analyzing skill gap against a job."""
    job_id: uuid.UUID


class ChatMessage(BaseModel):
    """Schema for chatbot message."""
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chatbot response."""
    reply: str
    suggestions: Optional[List[str]] = []


class EmailRequest(BaseModel):
    """Schema for email generation."""
    job_id: uuid.UUID
    email_type: str = "cold"  # cold, followup
    custom_instructions: Optional[str] = None


class EmailResponse(BaseModel):
    """Schema for generated email."""
    subject: str
    body: str
    job_title: str
    company: str
