import traceback

from fastapi import APIRouter, Depends, HTTPException

from app.ai.ai_schema import (
    AIAnalysisRequest,
    AIAnalysisResponse,
)
from app.ai.ai_service import analyze_stock
from app.ai.chat_schema import (
    AIChatRequest,
    AIChatResponse,
)
from app.ai.chat_service import (
    chat_with_finpilot,
)
from app.models.user import User
from app.schemas.common_schema import APIResponse
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ============================================================
# EXISTING STOCK ANALYSIS
# ============================================================

@router.post(
    "/analyze",
    response_model=APIResponse[AIAnalysisResponse],
    summary="Analyze Stock with FinPilot AI",
)
def analyze_ai_stock(
    request: AIAnalysisRequest,
    current_user: User = Depends(
        get_current_user
    ),
):
    try:

        analysis = analyze_stock(
            request
        )

        return {
            "success": True,
            "message":
                "AI analysis completed successfully.",
            "data": analysis,
        }

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )


# ============================================================
# NEW FINPILOT CHATBOT
# ============================================================

@router.post(
    "/chat",
    response_model=APIResponse[AIChatResponse],
    summary="Chat with FinPilot AI",
)
def chat_with_ai(
    request: AIChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        result = chat_with_finpilot(
            request
        )

        return {
            "success": True,
            "message":
                "FinPilot AI response generated successfully.",
            "data": result,
        }

    except HTTPException:
        raise

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )