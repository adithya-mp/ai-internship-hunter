"""
Skill Analyzer Service
Analyzes skill gaps and provides learning recommendations.
"""

import logging
from typing import List
from services.ai_engine import generate_json

logger = logging.getLogger(__name__)

SKILL_ANALYSIS_PROMPT = """Analyze the skill gap between a candidate and a job requirement.

**Candidate's Skills:** {user_skills}
**Job Required Skills:** {required_skills}
**Job Title:** {job_title}

Respond with a JSON object:
{{
    "matching_skills": ["skills the candidate has that match the job"],
    "missing_skills": ["skills the candidate lacks for this job"],
    "match_percentage": 75.0,
    "recommendations": [
        {{
            "skill": "Missing Skill Name",
            "reason": "Why this skill is important for the role",
            "resources": ["Suggested course or resource 1", "Resource 2"],
            "priority": "high"
        }}
    ],
    "learning_roadmap": [
        {{
            "week": "Week 1-2",
            "focus": "Skill to learn",
            "activities": ["What to do"]
        }}
    ]
}}

Be specific and practical with recommendations. Prioritize the most impactful skills first."""


async def analyze_skill_gap(
    user_skills: List[str],
    required_skills: List[str],
    job_title: str,
) -> dict:
    """
    Analyze the gap between user skills and job requirements.
    Returns structured analysis with recommendations.
    """
    prompt = SKILL_ANALYSIS_PROMPT.format(
        user_skills=", ".join(user_skills) if user_skills else "No skills listed",
        required_skills=", ".join(required_skills) if required_skills else "General skills",
        job_title=job_title,
    )

    result = await generate_json(prompt)

    if not result:
        # Fallback analysis
        user_set = set(s.lower() for s in user_skills)
        req_set = set(s.lower() for s in required_skills)
        matching = user_set & req_set
        missing = req_set - user_set

        match_pct = (len(matching) / max(len(req_set), 1)) * 100

        result = {
            "matching_skills": list(matching),
            "missing_skills": list(missing),
            "match_percentage": round(match_pct, 1),
            "recommendations": [
                {
                    "skill": skill,
                    "reason": f"Required for the {job_title} role",
                    "resources": [f"Search for '{skill} tutorial' on YouTube or Coursera"],
                    "priority": "high" if i < 3 else "medium",
                }
                for i, skill in enumerate(missing)
            ],
            "learning_roadmap": [],
        }

    return result
