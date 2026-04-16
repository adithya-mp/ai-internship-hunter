"""
News Scraper Service
Fetches tech news and hiring trends for the learning module.
"""

import logging
from typing import List
from services.ai_engine import generate_json

logger = logging.getLogger(__name__)


async def get_tech_trends() -> List[dict]:
    """
    Generate current tech hiring trends and news using AI.
    Returns a list of trend items.
    """
    prompt = """Generate a list of 8 current technology and hiring trends relevant to students 
and early-career professionals looking for internships. For each trend, provide:

{{
    "trends": [
        {{
            "title": "Trend Title",
            "summary": "2-3 sentence summary of the trend",
            "category": "AI/ML | Web Dev | Cloud | Data | Mobile | Cybersecurity | DevOps",
            "impact": "high | medium",
            "skills_to_learn": ["Skill1", "Skill2"],
            "action_item": "What the student should do about this trend"
        }}
    ]
}}

Make them realistic, current, and actionable. Focus on trends like:
- AI/ML adoption in companies
- Most in-demand programming languages
- Remote work / hybrid trends
- Startup hiring patterns
- Emerging technologies (blockchain, quantum, etc.)
- Industry-specific trends (fintech, healthtech, etc.)"""

    result = await generate_json(prompt)

    if result and "trends" in result:
        return result["trends"]

    # Fallback trends
    return [
        {
            "title": "AI & Machine Learning Dominate Hiring",
            "summary": "Companies across all sectors are seeking talent with AI/ML skills. Python, TensorFlow, and PyTorch are the most sought-after technologies.",
            "category": "AI/ML",
            "impact": "high",
            "skills_to_learn": ["Python", "TensorFlow", "PyTorch", "LLM APIs"],
            "action_item": "Build a project using a popular LLM API like Gemini or OpenAI.",
        },
        {
            "title": "Full-Stack Development Remains King",
            "summary": "React + Node.js continues to be the most popular tech stack for web development internships. TypeScript adoption is at an all-time high.",
            "category": "Web Dev",
            "impact": "high",
            "skills_to_learn": ["React", "TypeScript", "Node.js", "Next.js"],
            "action_item": "Build a full-stack project and deploy it to showcase your skills.",
        },
        {
            "title": "Cloud Skills Are Non-Negotiable",
            "summary": "AWS, Azure, and GCP certifications significantly boost internship applications. Companies expect even interns to understand cloud basics.",
            "category": "Cloud",
            "impact": "high",
            "skills_to_learn": ["AWS", "Docker", "Kubernetes", "CI/CD"],
            "action_item": "Get started with AWS Free Tier and deploy a personal project.",
        },
        {
            "title": "Data Engineering Internships Surge",
            "summary": "With data-driven decision making becoming standard, companies need more data engineers. SQL, Python, and ETL pipeline skills are essential.",
            "category": "Data",
            "impact": "medium",
            "skills_to_learn": ["SQL", "Apache Spark", "Airflow", "dbt"],
            "action_item": "Learn SQL deeply and build a data pipeline project.",
        },
        {
            "title": "Cybersecurity Talent Shortage Continues",
            "summary": "The cybersecurity gap is widening, creating opportunities for students. Even basic security knowledge makes candidates stand out.",
            "category": "Cybersecurity",
            "impact": "medium",
            "skills_to_learn": ["Network Security", "OWASP", "Penetration Testing"],
            "action_item": "Complete a beginner CTF (Capture The Flag) challenge.",
        },
        {
            "title": "Remote-First Internships Expand Options",
            "summary": "More companies offer fully remote internships, opening opportunities beyond geographic limits. Communication and self-management skills are crucial.",
            "category": "General",
            "impact": "medium",
            "skills_to_learn": ["Git", "Agile", "Communication"],
            "action_item": "Contribute to open source projects to demonstrate remote collaboration skills.",
        },
    ]
