import logging
from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import FoodExtractionRequest, FoodExtractionResponse
from app.services.gemini_service import extract_food_with_gemini

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/extract-food",
    response_model=FoodExtractionResponse,
    summary="Extract structured food donation details from natural language using Gemini 2.5 Flash",
    description="Parses a donor's unstructured text description and extracts verified donation fields (food name, quantity, unit, type, cooked time) with zero hallucination."
)
async def extract_food(payload: FoodExtractionRequest):
    """
    Accepts natural-language description and returns structured donation details
    using Gemini 2.5 Flash (with fallback to local rule-based parsing if offline or unconfigured).
    """
    description = payload.description.strip()
    if not description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description cannot be empty."
        )

    try:
        result = await extract_food_with_gemini(description)
        return result
    except Exception as e:
        logger.error(f"Unexpected error during food extraction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to extract details. Please enter the information manually."
        )
