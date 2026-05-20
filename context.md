# ApplyIQ Project Context

## Overview
ApplyIQ is an AI-powered internship automation platform. It matches job listings from LinkedIn, Internshala, and Unstop against a candidate's profile and helps generate tailored resumes and cover letters using Google Gemini API.

## Technical Stack
- **Frontend**: React + Vite + TailwindCSS + Zustand
- **Backend**: FastAPI + SQLite (SQLAlchemy/aiosqlite)
- **AI**: Google Gemini API (`gemini-2.0-flash` for generation, `text-embedding-004` for matching)
- **Scraper**: Automated job scraper scheduler (LinkedIn, Internshala, Unstop)

## Active Tasks & Requirements
1. **Change 1 — Auth**: Implement `/signup` and `/signin` pages with Google & LinkedIn OAuth, Zustand persistent auth context, and a protected route HOC wrapper.
2. **Change 2 — Auto Job ID/URL Fetching**: Extract job ID and listing URL directly from job boards' API response (LinkedIn, Indeed, Internshala) and pass them automatically to resume/cover letter generator.
3. **Change 3 — AI Resume Generation**: Dual-source approach (scraped patterns for company/role from Gemini + JD inference) for resume generation. Complete, ATS-optimized, downloadable ReportLab PDF.
4. **Change 4 — AI Cover Letter Generation**: Personalized cover letter (3-4 paragraphs) using company name, role, user profile, and JD signals.
5. **Change 5 — My Dashboard Tab**: `/dashboard` route with inline-editable personal details, Gemini-powered recommended skills, and HTML5 Drag & Drop file uploads (stored in IndexedDB/localStorage).

## Current Stage
Researching the existing codebase to form an implementation plan. We are currently defining the design and implementation details in `implementation_plan.md`.
