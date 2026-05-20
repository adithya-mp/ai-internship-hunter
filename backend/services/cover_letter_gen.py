"""
Cover Letter Generator Service
Creates personalized, professional cover letters using AI.
"""

import logging
from services.ai_engine import generate_text

logger = logging.getLogger(__name__)

import json
from services.ai_engine import generate_text, generate_json

logger = logging.getLogger(__name__)

TEMPLATE_ANALYSIS_PROMPT = """Analyze this job description and identify the cover letter tone, structure, length constraints, and alignment signals favored by hiring managers at this company or industry.

**Job Title:** {job_title}
**Company:** {company}
**Job Description:**
{job_description}

Provide a JSON response containing:
{{
    "recommended_tone": "Describe the cover letter tone (e.g., enthusiastic yet professional, product-focused, engineering-driven)",
    "key_focus_points": ["point 1", "point 2"],
    "structure_suggestions": "Specific layout/paragraphs structure (e.g., open with project X, focus on company values in para 3)",
    "industry_keywords": ["keyword 1", "keyword 2"]
}}
"""

COVER_LETTER_PROMPT = """Write a professional cover letter for the following position using the provided template analysis signals.

**Job Title:** {job_title}
**Company:** {company}
**Job Description:** {job_description}
**Required Skills:** {required_skills}

**Template Analysis Signals:**
- Recommended Tone: {recommended_tone}
- Key Focus Points: {key_focus_points}
- Structure Suggestions: {structure_suggestions}
- Industry Keywords: {industry_keywords}

**About the Candidate:**
- Name: {user_name}
- Background: {bio}
- Key Skills: {user_skills}
- Notable Experience: {experience_summary}

{custom_instructions}

**Cover Letter Requirements:**
1. Professional yet confident tone aligning with the Template Analysis recommended tone.
2. Open with a compelling hook — why you're excited about this specific role
3. Paragraph 2: Why you're a great fit — connect your skills/experience to their requirements, incorporating the key focus points and industry keywords.
4. Paragraph 3: Why this company — show you've researched them
5. Close with an impact mindset — what you'll bring to the team
6. Keep it under 350 words (typically 3-4 paragraphs)
7. Do NOT use markdown formatting, just plain text with paragraphs
8. Do NOT include placeholder brackets like [Your Name] — use the actual candidate info provided
9. Sign off with the candidate's actual name: {user_name}"""


async def analyze_cover_letter_template(job_title: str, company: str, job_description: str) -> dict:
    """Analyze job requirements to extract optimal cover letter design and signals."""
    prompt = TEMPLATE_ANALYSIS_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:3000]
    )
    system_prompt = "You are an expert career advisor. Always respond in valid JSON."
    try:
        result = await generate_json(prompt, system_prompt)
        return result or {}
    except Exception as e:
        logger.error(f"Error analyzing cover letter template: {e}")
        return {}


async def generate_cover_letter(
    job_title: str,
    company: str,
    job_description: str,
    required_skills: list,
    user_profile: dict,
    custom_instructions: str = "",
) -> str:
    """
    Generate a personalized cover letter.
    Returns the cover letter text.
    """
    # 1. Step 1 - Analyze Template
    template_signals = await analyze_cover_letter_template(job_title, company, job_description)

    # Build experience summary
    experience_summary = "Early-career professional"
    if user_profile.get("experience"):
        exp_items = []
        for exp in user_profile["experience"][:3]:
            exp_items.append(f"{exp.get('title', '')} at {exp.get('company', '')}")
        experience_summary = "; ".join(exp_items)

    prompt = COVER_LETTER_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:2000],
        required_skills=", ".join(required_skills or []),
        recommended_tone=template_signals.get("recommended_tone", "professional, confident"),
        key_focus_points=", ".join(template_signals.get("key_focus_points", [])),
        structure_suggestions=template_signals.get("structure_suggestions", "3-4 paragraphs tailored to job details"),
        industry_keywords=", ".join(template_signals.get("industry_keywords", [])),
        user_name=user_profile.get("full_name", "Candidate"),
        bio=user_profile.get("bio", "Technology professional with a passion for innovation"),
        user_skills=", ".join(user_profile.get("skills", [])),
        experience_summary=experience_summary,
        custom_instructions=f"Additional instructions: {custom_instructions}" if custom_instructions else "",
    )

    result = await generate_text(prompt, temperature=0.7)
    return result.strip()
