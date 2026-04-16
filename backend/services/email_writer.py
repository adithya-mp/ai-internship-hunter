"""
Email Writer Service
Generates personalized cold emails and follow-ups to recruiters.
"""

import logging
from services.ai_engine import generate_text

logger = logging.getLogger(__name__)

COLD_EMAIL_PROMPT = """Write a professional cold email to a recruiter about the following position:

**Job Title:** {job_title}
**Company:** {company}
**Job Description:** {job_description}

**About the Candidate:**
- Name: {user_name}
- Key Skills: {user_skills}
- Notable Experience: {experience_summary}

{custom_instructions}

**Email Requirements:**
1. Subject line (start with "Subject: ")
2. Professional, concise, and engaging tone
3. Open with a personalized hook — reference the company or role specifically
4. Briefly highlight 2-3 relevant qualifications
5. Clear call to action (request for conversation/interview)
6. Keep under 200 words
7. Sign off with the candidate's name
8. Do NOT use placeholder brackets — use actual info provided
9. Separate subject from body with a blank line"""

FOLLOWUP_EMAIL_PROMPT = """Write a professional follow-up email for a job application:

**Job Title:** {job_title}
**Company:** {company}
**Candidate Name:** {user_name}

{custom_instructions}

**Requirements:**
1. Start with "Subject: " line
2. Reference the original application
3. Reaffirm interest politely
4. Keep it under 150 words
5. Professional and respectful tone
6. Do NOT be pushy
7. Sign off with the candidate's name"""


async def generate_cold_email(
    job_title: str,
    company: str,
    job_description: str,
    user_profile: dict,
    custom_instructions: str = "",
) -> dict:
    """
    Generate a cold email to a recruiter.
    Returns dict with subject and body.
    """
    experience_summary = "Early-career professional"
    if user_profile.get("experience"):
        exp_items = [f"{e.get('title', '')} at {e.get('company', '')}" for e in user_profile["experience"][:2]]
        experience_summary = "; ".join(exp_items)

    prompt = COLD_EMAIL_PROMPT.format(
        job_title=job_title,
        company=company,
        job_description=job_description[:1500],
        user_name=user_profile.get("full_name", "Candidate"),
        user_skills=", ".join(user_profile.get("skills", [])),
        experience_summary=experience_summary,
        custom_instructions=f"Additional instructions: {custom_instructions}" if custom_instructions else "",
    )

    result = await generate_text(prompt, temperature=0.6)
    return _parse_email(result, job_title, company)


async def generate_followup_email(
    job_title: str,
    company: str,
    user_name: str,
    custom_instructions: str = "",
) -> dict:
    """
    Generate a follow-up email.
    Returns dict with subject and body.
    """
    prompt = FOLLOWUP_EMAIL_PROMPT.format(
        job_title=job_title,
        company=company,
        user_name=user_name,
        custom_instructions=f"Additional instructions: {custom_instructions}" if custom_instructions else "",
    )

    result = await generate_text(prompt, temperature=0.5)
    return _parse_email(result, job_title, company)


async def generate_email(
    job_title: str,
    company: str,
    email_type: str,
    user_profile: dict,
    custom_instructions: str = ""
) -> str:
    """
    Main entry point for email generation.
    Returns the full string content of the email.
    """
    if email_type == "cold":
        # Cold emails use job description (mocking placeholder here)
        result = await generate_cold_email(
            job_title=job_title,
            company=company,
            job_description="Referencing the latest job posting",
            user_profile=user_profile,
            custom_instructions=custom_instructions
        )
    else:
        result = await generate_followup_email(
            job_title=job_title,
            company=company,
            user_name=user_profile.get("full_name", "Candidate"),
            custom_instructions=custom_instructions
        )
    
    # The router expects a combined string to parse itself, or we can format it here
    return f"Subject: {result['subject']}\n\n{result['body']}"


def _parse_email(text: str, job_title: str, company: str) -> dict:
    """Parse email text into subject and body."""
    lines = text.strip().split("\n")
    subject = f"Interest in {job_title} Position at {company}"
    body = text

    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line[8:].strip()
            body = "\n".join(lines[i + 1:]).strip()
            break

    return {
        "subject": subject,
        "body": body,
        "job_title": job_title,
        "company": company,
    }
