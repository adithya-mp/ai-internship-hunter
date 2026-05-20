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

TEMPLATE_ANALYSIS_PROMPT = """Analyze this job posting and identify the optimal resume design, sections, keyword strategies, and achievements/skills prioritized by hiring teams at this company or industry.

**Job Title:** {job_title}
**Company:** {company}
**Job Description:**
{job_description}

Provide a JSON response containing:
{{
    "accepted_patterns": "Describe the resume format/template typically favored (e.g. chronological, project-heavy, core competence highlight)",
    "keywords": ["list", "of", "high-priority", "keywords"],
    "formatting_conventions": "Recommended section layout or styling rules (e.g., technical skills at top, project-focused)",
    "tone_focus": "The specific tone to emphasize (e.g., highly quantitative, research-driven, product-oriented)",
    "bullet_recommendations": "Advice on how to phrase bullet points for experience/projects to appeal to this company's culture"
}}
"""

RESUME_GENERATE_PROMPT = """Create a tailored resume for the following job using the provided Recruiter Template Analysis and candidate profile.

**Job Title:** {job_title}
**Company:** {company}
**Job Description:** {job_description}
**Required Skills:** {required_skills}

**Recruiter Template Analysis (Signals to follow):**
- Accepted Patterns: {accepted_patterns}
- High-Priority Keywords: {keywords}
- Formatting/Section Layout: {formatting_conventions}
- Tone Focus: {tone_focus}
- Bullet Phrasing Recommendations: {bullet_recommendations}

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
- Align content to the Recruiter Template Analysis guidelines.
- Integrate the high-priority keywords naturally across experience, projects, and skills.
- Structure bullet points using strong action verbs and include metrics where possible.
- Return only a valid JSON object matching the schema. Do not truncate the result, generate a complete, full-length resume."""


async def analyze_job_template(job_title: str, company: str, job_description: str) -> dict:
    """Analyze the target job to extract resume design signals."""
    prompt = TEMPLATE_ANALYSIS_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:3000]
    )
    system_prompt = "You are a senior recruiter analyzing hiring patterns. Always respond in valid JSON."
    try:
        result = await generate_json(prompt, system_prompt)
        return result or {}
    except Exception as e:
        logger.error(f"Error analyzing job template: {e}")
        return {}


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
    # 1. Step 1 - Analyze Template
    template_signals = await analyze_job_template(job_title, company, job_description)

    # 2. Step 2 - Generate Resume
    prompt = RESUME_GENERATE_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:2500],  # Limit to stay within budget
        required_skills=", ".join(required_skills or []),
        accepted_patterns=template_signals.get("accepted_patterns", " chronological / tech-stack focused"),
        keywords=", ".join(template_signals.get("keywords", [])),
        formatting_conventions=template_signals.get("formatting_conventions", "technical skills, experience, projects"),
        tone_focus=template_signals.get("tone_focus", "confident, achievement-oriented"),
        bullet_recommendations=template_signals.get("bullet_recommendations", "start with action verbs, highlight tech stack"),
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
    # Also add keywords from template analysis
    keywords = set(template_signals.get("keywords", []))
    merged_skills = list(job_skills.union(user_skills).union(keywords))[:20] # Cap at 20

    # Ensure all required keys exist
    result.setdefault("summary", "")
    result.setdefault("experience", [])
    result.setdefault("education", [])
    result["skills"] = list(set(result.get("skills", []) + merged_skills))[:20]
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
