from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from app.db.client import get_db
from app.services.openai_service import generate_completion
from app.models.responses import AgentResponse

router = APIRouter()
security = HTTPBearer()

class ComponentBase(BaseModel):
    name: str
    type: str
    requirements: Dict[str, Any]
    metadata: Dict[str, Any] = {}

class ComponentCreate(ComponentBase):
    project_id: UUID

class Component(ComponentBase):
    id: UUID
    project_id: UUID
    code: str
    created_at: datetime
    updated_at: datetime

class GenerateRequest(BaseModel):
    requirements: Dict[str, Any]
    design_tokens: Dict[str, Any]
    component_type: str

COMPONENT_SYSTEM_PROMPT = """
You are a React component generator. Generate a well-structured, accessible, and 
reusable component based on the requirements and design tokens provided.
Follow these guidelines:
1. Use TypeScript
2. Include proper PropTypes
3. Follow React best practices
4. Include comments
5. Implement error handling
"""

@router.post("/generate", response_model=AgentResponse)
async def generate_component(
    request: GenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        prompt = f"""
        Component Type: {request.component_type}
        Requirements: {request.requirements}
        Design Tokens: {request.design_tokens}
        
        Generate a complete React component implementation.
        """
        
        result = await generate_completion(
            prompt=prompt,
            config_type='code',
            system_message=COMPONENT_SYSTEM_PROMPT
        )
        
        return AgentResponse(
            status=200,
            data={"code": result["content"]},
            metadata=result["metadata"]
        )
    except Exception as e:
        return AgentResponse(
            status=400,
            error=str(e),
            metadata={"processingTime": 0.0}
        )

@router.post("/", response_model=Component)
async def create_component(
    component: ComponentCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db = await get_db()
    try:
        now = datetime.utcnow()
        new_component = {
            "name": component.name,
            "type": component.type,
            "project_id": component.project_id,
            "requirements": component.requirements,
            "metadata": component.metadata,
            "created_at": now,
            "updated_at": now
        }
        
        result = db.table('components').insert(new_component).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}/components", response_model=List[Component])
async def list_components(
    project_id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    db = await get_db()
    try:
        components = db.table('components').select("*").eq('project_id', project_id).execute()
        return components.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 