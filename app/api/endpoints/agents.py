from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.openai_service import generate_completion
from app.models.responses import AgentResponse

router = APIRouter()
security = HTTPBearer()

class AgentRequest(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class AgentResponse(BaseModel):
    status: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any]

REQUIREMENTS_SYSTEM_PROMPT = """
You are a requirements analysis expert. Analyze the given requirements and break them down into:
1. Functional requirements
2. Technical specifications
3. UI/UX requirements
4. Potential challenges
Provide a structured JSON response.
"""

DESIGN_SYSTEM_PROMPT = """
You are a UI/UX design expert. Based on the requirements, generate:
1. Component hierarchy
2. Design system tokens
3. Layout structure
4. Interactive elements
Provide a structured JSON response with detailed design specifications.
"""

@router.post("/requirements", response_model=AgentResponse)
async def process_requirements(
    request: AgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        result = await generate_completion(
            prompt=request.content,
            config_type='requirements',
            system_message=REQUIREMENTS_SYSTEM_PROMPT
        )
        
        return AgentResponse(
            status=200,
            data={"analysis": result["content"]},
            metadata=result["metadata"]
        )
    except Exception as e:
        return AgentResponse(
            status=400,
            error=str(e),
            metadata={"processingTime": 0.0}
        )

@router.post("/design", response_model=AgentResponse)
async def generate_design(
    request: AgentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        result = await generate_completion(
            prompt=request.content,
            config_type='design',
            system_message=DESIGN_SYSTEM_PROMPT
        )
        
        return AgentResponse(
            status=200,
            data={"design": result["content"]},
            metadata=result["metadata"]
        )
    except Exception as e:
        return AgentResponse(
            status=400,
            error=str(e),
            metadata={"processingTime": 0.0}
        ) 