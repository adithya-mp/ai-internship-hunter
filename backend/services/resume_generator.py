"""
Resume Generator Service
Creates ATS-optimized, tailored resumes using AI.
"""

import json
import logging
from typing import Optional

from services.ai_engine import generate_json, generate_text

logger = logging.getLogger(__name__)

# ─── Prompt Templates ───

RESUME_SYSTEM_PROMPT = """You are an expert resume writer specializing in tech internships and early-career roles.
You create ATS-optimized resumes that emphasize:
- Strong action verbs (Developed, Engineered, Optimized, Implemented, Led, Designed)
- Quantifiable achievements (increased X by Y%, reduced Z by N hours)
- Keywords matching the job description
- Clean, professional formatting

ALWAYS respond in valid JSON format."""

RESUME_GENERATE_PROMPT = """Create a tailored resume for the following job:

**Job Title:** {job_title}
**Company:** {company}
**Job Description:** {job_description}
**Required Skills:** {required_skills}

**Candidate Profile:**
- Name: {user_name}
- Bio: {bio}
- Skills: {user_skills}
- Experience: {experience}
- Education: {education}
- Projects: {projects}

{custom_instructions}

Generate a JSON resume with this structure:
{{
    "summary": "2-3 sentence professional summary tailored to this role",
    "experience": [
        {{
            "title": "Role Title",
            "company": "Company Name",
            "duration": "Start - End",
            "bullets": ["Achievement 1 with metrics", "Achievement 2 with action verbs"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree",
            "institution": "University",
            "year": "Year",
            "gpa": "GPA if available"
        }}
    ],
    "skills": ["Skill1", "Skill2"],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description emphasizing relevant tech and impact"
        }}
    ],
    "certifications": ["Cert1"],
    "achievements": ["Achievement1"]
}}

IMPORTANT:
- Tailor every section to match the job requirements
- Use strong action verbs
- Include quantifiable metrics where possible
- Prioritize skills that match the job description
- Make the summary compelling and specific to this role"""


async def generate_resume(
    job_title: str,
    company: str,
    job_description: str,
    required_skills: list,
    user_profile: dict,
    custom_instructions: str = "",
) -> dict:
    """
    Generate a tailored resume based on job description and user profile.
    Returns structured resume content as a dict.
    """
    prompt = RESUME_GENERATE_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:3000],  # Limit for token budget
        required_skills=", ".join(required_skills or []),
        user_name=user_profile.get("full_name", "Candidate"),
        bio=user_profile.get("bio", "Technology professional"),
        user_skills=", ".join(user_profile.get("skills", [])),
        experience=json.dumps(user_profile.get("experience", []), indent=2),
        education=json.dumps(user_profile.get("education", []), indent=2),
        projects=json.dumps(user_profile.get("projects", []), indent=2),
        custom_instructions=f"Additional instructions: {custom_instructions}" if custom_instructions else "",
    )

    logger.info(f"AI generation request for {job_title} at {company}")
    result = await generate_json(prompt, RESUME_SYSTEM_PROMPT)

    # Validate and ensure required fields
    if not result:
        logger.warning("AI generation failed, using fallback resume content")
        result = _get_fallback_resume(user_profile, job_title, company)

    # Logic to merge skills: use job-required skills + relevant user profile skills
    user_skills = set(user_profile.get("skills", []))
    job_skills = set(required_skills or [])
    merged_skills = list(job_skills.union(user_skills))[:15] # Cap at 15

    # Ensure all required keys exist
    result.setdefault("summary", "")
    result.setdefault("experience", [])
    result.setdefault("education", [])
    result["skills"] = list(set(result.get("skills", []) + merged_skills))[:15]
    result.setdefault("projects", [])
    result.setdefault("certifications", [])
    result.setdefault("achievements", [])

    return result


def _get_fallback_resume(profile: dict, job_title: str, company: str) -> dict:
    """Fallback resume content when AI is unavailable."""
    return {
        "summary": f"Motivated professional seeking the {job_title} position at {company}. "
                   f"Strong technical foundation with hands-on project experience.",
        "experience": profile.get("experience", [
            {
                "title": "Software Development Intern",
                "company": "Tech Startup",
                "duration": "Jun 2024 - Aug 2024",
                "bullets": [
                    "Developed and maintained web applications using React and Node.js",
                    "Collaborated with a team of 5 engineers to deliver features on time",
                ]
            }
        ]),
        "education": profile.get("education", [
            {
                "degree": "B.Tech in Computer Science",
                "institution": "Engineering University",
                "year": "2024-2028",
            }
        ]),
        "skills": profile.get("skills", ["Python", "JavaScript", "React", "Node.js", "SQL"]),
        "projects": profile.get("projects", []),
        "certifications": [],
        "achievements": [],
    }
