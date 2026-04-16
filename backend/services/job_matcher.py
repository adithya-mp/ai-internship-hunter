"""
Job Matcher Service
Matches user profiles to job descriptions using vector embeddings and cosine similarity.
"""

import logging
import numpy as np
from typing import List, Tuple

from services.ai_engine import generate_embedding, generate_text

logger = logging.getLogger(__name__)


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


async def create_user_embedding(profile: dict) -> List[float]:
    """
    Create an embedding vector from user profile data.
    Combines skills, experience, education, and bio into a single text.
    """
    parts = []

    if profile.get("bio"):
        parts.append(profile["bio"])

    if profile.get("skills"):
        parts.append(f"Skills: {', '.join(profile['skills'])}")

    if profile.get("experience"):
        for exp in profile["experience"]:
            parts.append(f"Experience: {exp.get('title', '')} at {exp.get('company', '')}")

    if profile.get("education"):
        for edu in profile["education"]:
            parts.append(f"Education: {edu.get('degree', '')} from {edu.get('institution', '')}")

    if profile.get("projects"):
        for proj in profile["projects"]:
            parts.append(f"Project: {proj.get('name', '')}: {proj.get('description', '')}")

    text = ". ".join(parts) if parts else "General technology professional"
    return await generate_embedding(text)


async def create_job_embedding(job_title: str, description: str, skills: List[str]) -> List[float]:
    """Create an embedding vector from job listing data."""
    text = f"Job: {job_title}. Description: {description}. Required skills: {', '.join(skills or [])}"
    return await generate_embedding(text)


async def match_jobs(
    user_embedding: List[float],
    jobs: List[dict],
) -> List[dict]:
    """
    Match user profile against a list of jobs.
    Returns jobs sorted by match score with AI explanations.
    """
    scored_jobs = []

    for job in jobs:
        job_embedding = job.get("embedding")
        if not job_embedding:
            continue

        score = cosine_similarity(user_embedding, job_embedding)
        match_pct = round(score * 100, 1)

        scored_jobs.append({
            "job": job,
            "match_score": match_pct,
        })

    # Sort by match score descending
    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

    # Generate AI explanations for top matches
    for item in scored_jobs[:10]:
        try:
            explanation = await generate_match_explanation(
                item["job"].get("title", ""),
                item["job"].get("company", ""),
                item["job"].get("skills_required", []),
                item["match_score"],
            )
            item["match_reason"] = explanation
        except Exception:
            item["match_reason"] = f"Strong match ({item['match_score']}%) based on your skills and experience."

    return scored_jobs


async def generate_match_explanation(
    job_title: str,
    company: str,
    required_skills: List[str],
    score: float,
) -> str:
    """Generate an AI explanation for why a job matches the user."""
    prompt = (
        f"In 1-2 sentences, explain why a candidate might be a {score}% match for the "
        f"'{job_title}' role at {company}. Required skills: {', '.join(required_skills or ['general'])}. "
        f"Be specific and encouraging. Do not use markdown."
    )
    return await generate_text(prompt, temperature=0.5)
