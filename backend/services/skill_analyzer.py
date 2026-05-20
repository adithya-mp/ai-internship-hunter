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


RECOMMEND_SKILLS_PROMPT = """You are an expert career advisor.
Given a candidate's current skills and their target internship role, recommend 8 to 12 highly relevant skills they should acquire to stand out.
For each recommended skill, provide:
1. The skill name
2. A brief explanation of why it is critical for the target role
3. Market demand level (one of: High, Medium, Low)
4. Category (e.g. Frontend, Backend, DevOps, Data Science, Soft Skills)

**Candidate's Current Skills:** {user_skills}
**Target Internship Role:** {target_role}

Respond in valid JSON format matching this structure:
{{
    "recommendations": [
        {{
            "name": "Skill Name",
            "explanation": "Brief explanation of why it is critical for the target role",
            "demand": "High",
            "category": "Frontend"
        }}
    ]
}}
"""

async def recommend_skills_for_role(user_skills: List[str], target_role: str) -> dict:
    """Recommend skills for a user targeting a specific role."""
    prompt = RECOMMEND_SKILLS_PROMPT.format(
        user_skills=", ".join(user_skills) if user_skills else "No skills listed yet",
        target_role=target_role or "Software Engineering Intern"
    )
    result = await generate_json(prompt)
    if not result or "recommendations" not in result:
        # Fallback
        result = {
            "recommendations": [
                {"name": "Git & Version Control", "explanation": "Crucial for team collaboration in software engineering.", "demand": "High", "category": "DevTools"},
                {"name": "Docker", "explanation": "Industry standard for containerization and microservices development.", "demand": "High", "category": "DevOps"},
                {"name": "REST APIs", "explanation": "Essential for backend and frontend communication in modern web applications.", "demand": "High", "category": "Backend"},
                {"name": "SQL & Databases", "explanation": "Almost all roles require solid understanding of relational databases.", "demand": "High", "category": "Databases"},
                {"name": "TypeScript", "explanation": "Adds type safety to JavaScript, standard for modern frontend/fullstack roles.", "demand": "Medium", "category": "Frontend"},
                {"name": "Data Structures & Algorithms", "explanation": "Core foundation for passing technical interviews.", "demand": "High", "category": "CS Fundamentals"},
                {"name": "Testing (Jest/PyTest)", "explanation": "Writing unit tests shows maturity and code quality ownership.", "demand": "Medium", "category": "QA"},
                {"name": "Agile Methodology", "explanation": "Understand sprints, scrum, and collaboration frameworks.", "demand": "Medium", "category": "Soft Skills"},
            ]
        }
    return result


UPSKILL_PLAN_PROMPT = """You are an elite tech career coach.
Create a personalized upskilling plan and week-by-week learning roadmap for a candidate missing key skills for their target role.

**Candidate's Current Skills:** {user_skills}
**Target Role:** {target_role}
**Missing High Priority Skills:** {missing_skills}

Respond with a JSON object matching this structure:
{{
    "target_role": "Target role name",
    "missing_skills": ["List of missing skills analyzed"],
    "summary": "1-2 sentence career advice summary",
    "roadmap": [
        {{
            "duration": "Weeks 1-2",
            "skill": "Skill to acquire",
            "focus": "Core focus area details",
            "activities": [
                "Practical action step 1",
                "Practical action step 2"
            ],
            "resources": [
                "Specific course/tutorial name or link"
            ]
        }}
    ]
}}
"""

async def recommend_upskill_plan(user_skills: List[str], target_role: str, missing_skills: List[str]) -> dict:
    """Generate an upskilling learning roadmap using Gemini, or use a robust fallback."""
    prompt = UPSKILL_PLAN_PROMPT.format(
        user_skills=", ".join(user_skills) if user_skills else "No skills listed yet",
        target_role=target_role or "Software Engineering Intern",
        missing_skills=", ".join(missing_skills) if missing_skills else "Docker, Redis, AWS, System Design"
    )
    
    result = await generate_json(prompt)
    
    if not result or "roadmap" not in result:
        # High quality fallback
        result = {
            "target_role": target_role or "Software Engineering Intern",
            "missing_skills": missing_skills or ["Docker", "Redis", "AWS", "System Design"],
            "summary": "Acquiring these key DevOps and system scaling skills will elevate your profile from junior developer to a highly-coveted systems engineering intern.",
            "roadmap": [
                {
                    "duration": "Weeks 1-2",
                    "skill": "Docker",
                    "focus": "Containerization & Multi-service orchestration",
                    "activities": [
                        "Understand container lifecycle, images, and networking basics.",
                        "Write a optimized multi-stage Dockerfile for a FastAPI application.",
                        "Use Docker Compose to run local backend, frontend, and database services."
                    ],
                    "resources": [
                        "Docker & Containerization - freeCodeCamp on YouTube",
                        "Docker Official Get Started Guides"
                    ]
                },
                {
                    "duration": "Weeks 3-4",
                    "skill": "Redis",
                    "focus": "In-memory caching & Background message brokers",
                    "activities": [
                        "Learn Redis basic data structures: strings, hashes, lists, sets.",
                        "Integrate Redis cache into FastAPI routes to reduce db query latency.",
                        "Configure Redis as a task broker for asynchronous processing."
                    ],
                    "resources": [
                        "Redis University: RU101 Introduction to Redis",
                        "FastAPI Caching Patterns using Redis tutorials"
                    ]
                },
                {
                    "duration": "Weeks 5-6",
                    "skill": "AWS",
                    "focus": "Cloud deployment & Infrastructure basics",
                    "activities": [
                        "Learn AWS core services: EC2, S3, RDS, IAM, and VPC.",
                        "Manually deploy your FastAPI application on an EC2 instance with Nginx.",
                        "Create an S3 bucket to securely host user resumes and static assets."
                    ],
                    "resources": [
                        "AWS Certified Cloud Practitioner - freeCodeCamp on YouTube",
                        "AWS Console Sandbox Free Tier Exercises"
                    ]
                },
                {
                    "duration": "Weeks 7-8",
                    "skill": "System Design",
                    "focus": "High availability, load balancing & Database scaling",
                    "activities": [
                        "Learn architectural patterns: vertical vs horizontal scaling.",
                        "Understand load balancers (Nginx, ALBs) and rate limiters.",
                        "Study database indexing, read-replicas, and basic sharding concepts."
                    ],
                    "resources": [
                        "Grokking Modern System Design Interview on Educative",
                        "System Design Primer - Github Repository by Donne Martin"
                    ]
                }
            ]
        }
    return result

