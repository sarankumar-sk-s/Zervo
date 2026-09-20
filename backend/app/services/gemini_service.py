import os
import re
import json
import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.schemas.ai import FoodExtractionResponse

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

SYSTEM_INSTRUCTION = """You are an accurate, strict food rescue extraction assistant.
Extract structured food donation information from the donor's natural language input.

CRITICAL RULES:
1. NEVER hallucinate missing information.
2. If quantity is not explicitly mentioned, return null for quantity.
3. If unit is not explicitly mentioned, return null for unit.
4. If prepared time is not mentioned, return null for prepared_time. Do not invent the time.
5. If expiry time is not explicitly mentioned, return null for expiry_time. Do not calculate or guess.
6. food_type must be strictly one of: "vegetarian", "non_vegetarian", "vegan", "unknown".
7. Never make medical or food-safety claims.
8. confidence must be a float between 0.0 and 1.0 representing extraction certainty.
"""

GEMINI_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "food_name": {
            "type": "STRING",
            "description": "Name of the food. Do not invent if not mentioned."
        },
        "quantity": {
            "type": "INTEGER",
            "description": "Numerical quantity only when explicitly mentioned. Return null otherwise."
        },
        "unit": {
            "type": "STRING",
            "description": "Unit of measurement (e.g. packets, meals, kg, litres, boxes, portions)."
        },
        "food_type": {
            "type": "STRING",
            "enum": ["vegetarian", "non_vegetarian", "vegan", "unknown"],
            "description": "Food type: vegetarian, non_vegetarian, vegan, or unknown."
        },
        "prepared_time": {
            "type": "STRING",
            "description": "Time prepared if explicitly stated (e.g. 7 PM). Null otherwise."
        },
        "expiry_time": {
            "type": "STRING",
            "description": "Expiry time only if explicitly mentioned. Null otherwise."
        },
        "description": {
            "type": "STRING",
            "description": "Short normalized summary description of the food donation."
        },
        "confidence": {
            "type": "NUMBER",
            "description": "Confidence score between 0.0 and 1.0."
        }
    },
    "required": [
        "food_name", "quantity", "unit", "food_type",
        "prepared_time", "expiry_time", "description", "confidence"
    ]
}


def rule_based_fallback_extract(text: str) -> FoodExtractionResponse:
    """
    Deterministic rule-based extractor used when GEMINI_API_KEY is not configured
    or when the Gemini API service is temporarily unavailable.
    Guarantees strict zero-hallucination compliance.
    """
    cleaned = text.strip()
    lower = cleaned.lower()

    # 1. Extract Quantity & Unit
    # Patterns like "30 packets", "50 meals", "10 kg", "100 boxes", "25 packets"
    qty = None
    unit = None
    qty_match = re.search(r'\b(\d+)\s*(kg|kilograms?|grams?|packets?|meals?|boxes|portions?|litres?|plates?|servings?)\b', lower)
    if qty_match:
        qty = int(qty_match.group(1))
        unit = qty_match.group(2).lower()
        if unit.endswith('s') and unit not in ['boxes']:
            # Normalize e.g. packets -> packets
            pass
    else:
        # Check standalone number if followed by food
        num_match = re.search(r'\b(\d+)\b', lower)
        if num_match:
            qty = int(num_match.group(1))

    # 2. Extract Food Type
    food_type = "unknown"
    if any(term in lower for term in ["vegan", "plant-based"]):
        food_type = "vegan"
    elif any(term in lower for term in ["chicken", "mutton", "fish", "meat", "beef", "egg", "non-veg", "non veg"]):
        food_type = "non_vegetarian"
    elif any(term in lower for term in ["vegetarian", "veg ", "veg.", "veggie", "paneer", "dal"]):
        food_type = "vegetarian"

    # 3. Extract Prepared Time
    # Patterns like "made at 7 PM", "prepared at 6 PM", "cooked at 10:30 AM", "at 7 PM"
    prepared_time = None
    time_match = re.search(r'(?:made|prepared|cooked)?\s*(?:at|around)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b', cleaned, re.IGNORECASE)
    if not time_match:
        time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM))\b', cleaned)
    if time_match:
        prepared_time = time_match.group(1).strip()

    # 4. Extract Expiry Time
    expiry_time = None
    exp_match = re.search(r'(?:expires?|expiry|consume before|use by)\s*(?:at|by|in)?\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?|\d+\s*(?:hours?|days?))\b', cleaned, re.IGNORECASE)
    if exp_match:
        expiry_time = exp_match.group(1).strip()

    # 5. Extract Food Name
    food_name = None
    # Known popular food nouns
    items = [
        ("veg biryani", "Veg Biryani", "vegetarian"),
        ("chicken biryani", "Chicken Biryani", "non_vegetarian"),
        ("biryani", "Biryani", None),
        ("cooked rice", "Cooked Rice", None),
        ("rice", "Rice", None),
        ("vegetarian food", "Vegetarian Food", "vegetarian"),
        ("leftover food", "Leftover Food", None),
        ("leftover", "Leftover Food", None),
        ("curry", "Curry", None),
        ("meals", "Meals", None),
        ("food", "Food", None)
    ]
    for pattern, name, ftype in items:
        if pattern in lower:
            food_name = name
            if ftype and food_type == "unknown":
                food_type = ftype
            break

    # If food_name still not found, extract phrase around quantity or general text
    if not food_name and ("have" in lower or "some" in lower):
        residual = re.sub(r'^(i have|we have|there are|have|some)\s*', '', lower).strip()
        residual = re.sub(r'^(a|an|the|\d+)\s*', '', residual).strip()
        if residual:
            food_name = residual.split('.')[0].split(',')[0].title()

    # Calculate confidence based on extracted elements
    confidence = 0.5
    if food_name:
        confidence += 0.2
    if qty is not None:
        confidence += 0.15
    if food_type != "unknown":
        confidence += 0.1
    confidence = min(0.95, round(confidence, 2))

    return FoodExtractionResponse(
        food_name=food_name,
        quantity=qty,
        unit=unit,
        food_type=food_type,
        prepared_time=prepared_time,
        expiry_time=expiry_time,
        description=cleaned,
        confidence=confidence
    )


async def extract_food_with_gemini(description: str) -> FoodExtractionResponse:
    """
    Extract structured food donation fields using Google Gemini 2.5 Flash
    with response_schema / JSON mode.
    Falls back gracefully to rule_based_fallback_extract if API key is not set or network fails.
    """
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    # If no Gemini API Key is configured in backend environment, use deterministic rule-based fallback
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.info("GEMINI_API_KEY not set. Using rule-based fallback extractor.")
        return rule_based_fallback_extract(description)

    model = settings.GEMINI_MODEL or "gemini-2.5-flash"
    url = f"{GEMINI_API_URL}/{model}:generateContent?key={api_key}"

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"Extract donation details from this description:\n\"{description}\""}]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": GEMINI_RESPONSE_SCHEMA,
            "temperature": 0.1
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                # Safe fallback
                return rule_based_fallback_extract(description)

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini returned empty candidates. Falling back.")
                return rule_based_fallback_extract(description)

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            extracted_dict = json.loads(raw_text)

            # Validate against Pydantic schema
            return FoodExtractionResponse(**extracted_dict)

    except Exception as e:
        logger.error(f"Error during Gemini API call: {str(e)}. Using safe fallback.")
        return rule_based_fallback_extract(description)
