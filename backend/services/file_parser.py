"""
File Parser Service
Extracts text and structured data from PDF and DOCX files.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""


async def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""


async def parse_resume_text(text: str) -> dict:
    """
    Use AI to extract structured data from resume text.
    Returns dict with skills, experience, education, etc.
    """
    from services.ai_engine import generate_json

    prompt = f"""Extract structured information from this resume text. 
Return a JSON object with:
{{
    "skills": ["list", "of", "skills"],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Date Range",
            "bullets": ["Key achievement 1", "Key achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University",
            "year": "Year or Date Range"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description"
        }}
    ],
    "certifications": ["cert1", "cert2"],
    "contact": {{
        "email": "email if found",
        "phone": "phone if found"
    }}
}}

Resume text:
{text[:5000]}"""

    result = await generate_json(prompt)
    if not result:
        # Basic keyword extraction fallback
        result = {
            "skills": _extract_skills_basic(text),
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "contact": {},
        }
    return result


def _extract_skills_basic(text: str) -> list:
    """Basic keyword extraction for skills when AI is unavailable."""
    common_skills = [
        "python", "javascript", "typescript", "react", "node.js", "html", "css",
        "sql", "postgresql", "mongodb", "docker", "git", "aws", "azure",
        "java", "c++", "c#", "ruby", "go", "rust", "swift", "kotlin",
        "django", "flask", "fastapi", "express", "next.js", "vue.js", "angular",
        "machine learning", "deep learning", "data science", "ai",
        "figma", "photoshop", "ui/ux", "agile", "scrum",
    ]
    text_lower = text.lower()
    found = [skill for skill in common_skills if skill in text_lower]
    return found
