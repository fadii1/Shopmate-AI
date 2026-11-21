from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ToolCallRecord(BaseModel):
    tool: str
    parameters: Dict[str, Any]
    output: Any


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default-session"
    user_language: Optional[str] = None  # auto-detected if None


class ChatResponse(BaseModel):
    response: str
    language: str  # english, urdu, roman_urdu
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    session_id: str
    products: Optional[List[Dict[str, Any]]] = None
