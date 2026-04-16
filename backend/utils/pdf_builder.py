"""
PDF Builder Utility
Generates professional PDF resumes and cover letters using ReportLab.
"""

import os
import uuid
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from config import get_settings

settings = get_settings()


def _get_styles():
    """Create custom styles for the resume PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ResumeName",
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=HexColor("#1a1a2e"),
        fontName="Helvetica-Bold",
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="ResumeContact",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=HexColor("#4a4a6a"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontSize=13,
        leading=16,
        textColor=HexColor("#6c63ff"),
        fontName="Helvetica-Bold",
        spaceBefore=14,
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="JobTitle",
        fontSize=11,
        leading=14,
        fontName="Helvetica-Bold",
        textColor=HexColor("#1a1a2e"),
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="Company",
        fontSize=10,
        leading=13,
        textColor=HexColor("#4a4a6a"),
        fontName="Helvetica-Oblique",
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=10,
        leading=13,
        alignment=TA_JUSTIFY,
        textColor=HexColor("#2d2d44"),
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BulletPoint",
        fontSize=10,
        leading=13,
        leftIndent=18,
        textColor=HexColor("#2d2d44"),
        spaceAfter=3,
    ))

    return styles


def generate_resume_pdf(content: dict, user_name: str, user_email: str) -> str:
    """
    Generate a professional resume PDF from structured content.
    Returns the file path of the generated PDF.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"resume_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    styles = _get_styles()
    story = []

    # ─── Header ───
    story.append(Paragraph(user_name, styles["ResumeName"]))
    story.append(Paragraph(user_email, styles["ResumeContact"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=HexColor("#6c63ff")))
    story.append(Spacer(1, 8))

    # ─── Summary ───
    if content.get("summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles["SectionHeader"]))
        story.append(Paragraph(content["summary"], styles["BodyText2"]))

    # ─── Experience ───
    if content.get("experience"):
        story.append(Paragraph("EXPERIENCE", styles["SectionHeader"]))
        for exp in content["experience"]:
            title = exp.get("title", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            story.append(Paragraph(f"{title}", styles["JobTitle"]))
            story.append(Paragraph(f"{company} | {duration}", styles["Company"]))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", styles["BulletPoint"]))
            story.append(Spacer(1, 4))

    # ─── Education ───
    if content.get("education"):
        story.append(Paragraph("EDUCATION", styles["SectionHeader"]))
        for edu in content["education"]:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            year = edu.get("year", "")
            story.append(Paragraph(f"{degree}", styles["JobTitle"]))
            story.append(Paragraph(f"{institution} | {year}", styles["Company"]))
            story.append(Spacer(1, 4))

    # ─── Projects ───
    if content.get("projects"):
        story.append(Paragraph("PROJECTS", styles["SectionHeader"]))
        for proj in content["projects"]:
            name = proj.get("name", "")
            desc = proj.get("description", "")
            story.append(Paragraph(f"{name}", styles["JobTitle"]))
            story.append(Paragraph(desc, styles["BodyText2"]))
            story.append(Spacer(1, 4))

    # ─── Skills ───
    if content.get("skills"):
        story.append(Paragraph("SKILLS", styles["SectionHeader"]))
        skills_text = " • ".join(content["skills"])
        story.append(Paragraph(skills_text, styles["BodyText2"]))

    # ─── Certifications ───
    if content.get("certifications"):
        story.append(Paragraph("CERTIFICATIONS", styles["SectionHeader"]))
        for cert in content["certifications"]:
            story.append(Paragraph(f"• {cert}", styles["BulletPoint"]))

    # ─── Achievements ───
    if content.get("achievements"):
        story.append(Paragraph("ACHIEVEMENTS", styles["SectionHeader"]))
        for ach in content["achievements"]:
            story.append(Paragraph(f"• {ach}", styles["BulletPoint"]))

    doc.build(story)
    return filepath


def generate_cover_letter_pdf(content: str, user_name: str, company: str, role: str) -> str:
    """
    Generate a cover letter PDF.
    Returns the file path of the generated PDF.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"cover_letter_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=1 * inch,
        leftMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = _get_styles()
    story = []

    # Header
    story.append(Paragraph(user_name, styles["ResumeName"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor("#6c63ff")))
    story.append(Spacer(1, 20))

    # Title
    story.append(Paragraph(f"Cover Letter — {role} at {company}", styles["SectionHeader"]))
    story.append(Spacer(1, 12))

    # Body - split by paragraphs
    paragraphs = content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), styles["BodyText2"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    return filepath
