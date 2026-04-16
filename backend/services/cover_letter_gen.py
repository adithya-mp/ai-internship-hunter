"""
Cover Letter Generator Service
Creates personalized, professional cover letters using AI.
"""

import logging
from services.ai_engine import generate_text

logger = logging.getLogger(__name__)

COVER_LETTER_PROMPT = """Write a professional cover letter for the following position:

**Job Title:** {job_title}
**Company:** {company}
**Job Description:** {job_description}
**Required Skills:** {required_skills}

**About the Candidate:**
- Name: {user_name}
- Background: {bio}
- Key Skills: {user_skills}
- Notable Experience: {experience_summary}

{custom_instructions}

**Cover Letter Requirements:**
1. Professional yet confident tone
2. Open with a compelling hook — why you're excited about this specific role
3. Paragraph 2: Why you're a great fit — connect your skills/experience to their requirements
4. Paragraph 3: Why this company — show you've researched them
5. Close with an impact mindset — what you'll bring to the team
6. Keep it under 350 words
7. Do NOT use markdown formatting, just plain text with paragraphs
8. Do NOT include placeholder brackets like [Your Name] — use the actual candidate info provided
9. Sign off with the candidate's actual name: {user_name}"""


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
        user_name=user_profile.get("full_name", "Candidate"),
        bio=user_profile.get("bio", "Technology professional with a passion for innovation"),
        user_skills=", ".join(user_profile.get("skills", [])),
        experience_summary=experience_summary,
        custom_instructions=f"Additional instructions: {custom_instructions}" if custom_instructions else "",
    )

    result = await generate_text(prompt, temperature=0.7)
    return result.strip()
