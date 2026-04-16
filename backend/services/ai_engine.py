"""
AI Engine Service
Wrapper around Google Gemini API for all AI features.
Handles text generation, embeddings, and structured outputs.
"""

import json
import logging
from typing import Optional, List

import google.generativeai as genai
from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


# ─── Models ───
_chat_model = None
_embed_model = "models/text-embedding-004"


def _get_model():
    """Lazily initialize the Gemini generative model."""
    global _chat_model
    if _chat_model is None:
        _chat_model = genai.GenerativeModel("gemini-2.0-flash")
    return _chat_model


async def generate_text(prompt: str, system_instruction: str = "", temperature: float = 0.7) -> str:
    """
    Generate text using Gemini.
    Args:
        prompt: The user prompt
        system_instruction: System-level instruction
        temperature: Creativity level (0-1)
    Returns:
        Generated text string
    """
    try:
        model = _get_model()
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=4096,
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        # Return a fallback response for demo purposes
        return _fallback_response(prompt)


async def generate_json(prompt: str, system_instruction: str = "") -> dict:
    """
    Generate structured JSON output using Gemini.
    Returns parsed dict or fallback.
    """
    try:
        model = _get_model()
        full_prompt = (
            f"{system_instruction}\n\n{prompt}\n\n"
            "IMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, just raw JSON."
        )
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=4096,
            ),
        )
        text = response.text.strip()
        # Clean markdown code block if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {}
    except Exception as e:
        logger.error(f"Gemini JSON generation error: {e}")
        return {}


async def generate_embedding(text: str) -> List[float]:
    """
    Generate text embeddings using Gemini embedding model.
    Returns a list of floats (vector).
    """
    try:
        result = genai.embed_content(
            model=_embed_model,
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        # Return zero vector as fallback
        return [0.0] * 768


async def chat_completion(messages: List[dict], system_instruction: str = "") -> str:
    """
    Multi-turn chat completion.
    messages: list of {"role": "user"|"assistant", "content": "..."}
    """
    try:
        model = _get_model()
        # Build the full prompt from message history
        conversation = ""
        if system_instruction:
            conversation += f"System: {system_instruction}\n\n"
        for msg in messages:
            role = "Human" if msg["role"] == "user" else "Assistant"
            conversation += f"{role}: {msg['content']}\n\n"
        conversation += "Assistant:"

        response = model.generate_content(
            conversation,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return "I'm sorry, I encountered an error. Please try again."


def _fallback_response(prompt: str) -> str:
    """Provide a reasonable fallback when API is unavailable."""
    if "resume" in prompt.lower():
        return "A results-driven professional with strong technical skills and a passion for innovation. Experienced in software development with a focus on delivering high-quality solutions."
    elif "cover letter" in prompt.lower():
        return "Dear Hiring Manager,\n\nI am writing to express my strong interest in this position. With my background in technology and passion for innovation, I believe I would be a valuable addition to your team.\n\nThank you for your consideration.\n\nBest regards"
    elif "email" in prompt.lower():
        return "Subject: Interest in Open Position\n\nDear Recruiter,\n\nI hope this email finds you well. I am reaching out to express my interest in opportunities at your company.\n\nBest regards"
    return "I'd be happy to help you with that. Could you provide more details?"
