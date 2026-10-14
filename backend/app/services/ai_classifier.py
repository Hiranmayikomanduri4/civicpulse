"""
AI Civic Issue Image Classification Service.

Architecture:
1. Google Gemini 1.5 Flash Vision API (if GEMINI_API_KEY is configured in .env):
   Sends image bytes to Google Gemini API for state-of-the-art visual feature recognition.
2. Transparent Fallback Engine (when no API key is set):
   Uses local image metadata, color histogram analysis, and filename/context heuristics 
   to provide a working baseline prediction, clearly flagging that it is an explainable heuristic fallback.
"""
import os
import base64
import json
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageStat
import httpx
from backend.app.config import settings
from backend.app.schemas import VALID_CATEGORIES

logger = logging.getLogger("civicpulse.ai")


async def classify_issue_image(
    image_bytes: bytes,
    filename: Optional[str] = None,
    text_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify a civic issue image.
    Uses Google Gemini Vision API if key configured; otherwise uses transparent local fallback.
    """
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 10:
        try:
            return await _classify_with_gemini(image_bytes, text_hint)
        except Exception as e:
            logger.warning(f"Gemini Vision API request failed: {e}. Falling back to heuristic engine.")
            fallback_res = _classify_with_heuristic(image_bytes, filename, text_hint)
            fallback_res["explanation"] += f" (Note: Gemini API attempt encountered an error: {str(e)[:60]}...)"
            return fallback_res
    else:
        return _classify_with_heuristic(image_bytes, filename, text_hint)


async def _classify_with_gemini(image_bytes: bytes, text_hint: Optional[str] = None) -> Dict[str, Any]:
    """Invoke Google Gemini 1.5 Flash vision endpoint."""
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    
    # Allowed categories prompt
    categories_str = ", ".join(f'"{c}"' for c in VALID_CATEGORIES)
    prompt = (
        f"You are a civic infrastructure inspector AI. Inspect this image of a municipal problem. "
        f"Classify the issue into EXACTLY ONE of the following valid categories: [{categories_str}].\n"
        f"Additional context from citizen: '{text_hint or 'None'}'.\n\n"
        f"Respond ONLY with valid JSON in this exact structure without markdown backticks:\n"
        f'{{"predicted_category": "<category>", "confidence": <float 0.0 to 1.0>, "explanation": "<1-2 sentence reason>", "alternative_categories": [{{"category": "<alt1>", "confidence": <float>}}]}}'
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 256
        }
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract text response
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini API")
            
        text_content = candidates[0]["content"]["parts"][0]["text"].strip()
        
        # Clean potential markdown wrapping
        if text_content.startswith("```"):
            lines = text_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text_content = "\n".join(lines).strip()

        parsed = json.loads(text_content)
        category = parsed.get("predicted_category")
        if category not in VALID_CATEGORIES:
            category = "Other Infrastructure"

        return {
            "predicted_category": category,
            "confidence": round(float(parsed.get("confidence", 0.85)), 2),
            "explanation": parsed.get("explanation", "Detected civic infrastructure anomaly using Gemini Vision AI."),
            "is_ai_vision": True,
            "alternative_categories": parsed.get("alternative_categories", [])
        }


def _classify_with_heuristic(
    image_bytes: bytes,
    filename: Optional[str] = None,
    text_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transparent rule-based fallback classification.
    Clearly discloses that it is a fallback heuristic rather than a trained vision model.
    """
    filename_lower = (filename or "").lower()
    hint_lower = (text_hint or "").lower()
    combined_signals = f"{filename_lower} {hint_lower}"

    # Signal-based keyword matching on filename or user text hint
    if any(k in combined_signals for k in ["pothole", "road", "asphalt", "tar", "crack", "street"]):
        predicted = "Roads & Potholes"
        conf = 0.78
        reason = "Matched roadway infrastructure indicators (pothole/asphalt patterns)."
    elif any(k in combined_signals for k in ["trash", "garbage", "waste", "litter", "debris", "plastic"]):
        predicted = "Garbage & Sanitation"
        conf = 0.76
        reason = "Matched solid waste and sanitation keywords."
    elif any(k in combined_signals for k in ["light", "pole", "lamp", "dark", "bulb", "streetlight"]):
        predicted = "Street Lighting"
        conf = 0.80
        reason = "Matched municipal street lighting and illumination markers."
    elif any(k in combined_signals for k in ["water", "leak", "pipe", "drain", "flood", "sewage", "puddle"]):
        predicted = "Water & Drainage"
        conf = 0.82
        reason = "Matched municipal drainage or water leakage indicators."
    elif any(k in combined_signals for k in ["bin", "dustbin", "can", "container", "overflow"]):
        predicted = "Overflowing Dustbins"
        conf = 0.77
        reason = "Matched public receptacle and overflowing dustbin indicators."
    elif any(k in combined_signals for k in ["bench", "sign", "graffiti", "fence", "wall", "railing", "bus stop"]):
        predicted = "Public Property Damage"
        conf = 0.72
        reason = "Matched public furniture or municipal fixture markers."
    elif any(k in combined_signals for k in ["tree", "branch", "park", "grass", "plant"]):
        predicted = "Parks & Environment"
        conf = 0.75
        reason = "Matched municipal park and greenery indicators."
    else:
        # Image brightness and color profile fallback
        try:
            import io
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            stat = ImageStat.Stat(img)
            brightness = sum(stat.mean) / 3.0
            
            # Low light image might be street lighting
            if brightness < 60:
                predicted = "Street Lighting"
                conf = 0.65
                reason = "Low-light night imagery profile detected; suggests street lighting review."
            else:
                predicted = "Roads & Potholes"
                conf = 0.60
                reason = "General street-level imagery profile detected."
        except Exception:
            predicted = "Roads & Potholes"
            conf = 0.55
            reason = "Default civic roadway category selected for review."

    explanation = (
        f"{reason} (Fallback Engine: GEMINI_API_KEY is not configured. "
        f"This is an explainable heuristic, not a trained ML vision model. "
        f"Please verify or select your category before submitting)."
    )

    alternatives = [
        {"category": c, "confidence": 0.45}
        for c in VALID_CATEGORIES if c != predicted
    ][:3]

    return {
        "predicted_category": predicted,
        "confidence": conf,
        "explanation": explanation,
        "is_ai_vision": False,
        "alternative_categories": alternatives
    }
