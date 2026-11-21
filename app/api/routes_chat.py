from fastapi import APIRouter, HTTPException
from app.schemas.agent import ChatRequest, ChatResponse
from app.agent.core import khareed_agent

router = APIRouter(prefix="/chat", tags=["Chat & Agent"])


@router.post("", response_model=ChatResponse)
async def chat_with_khareed(request: ChatRequest):
    """Chat endpoint communicating with the Khareed shopping agent."""
    try:
        response = await khareed_agent.chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Khareed Agent error: {str(e)}")
