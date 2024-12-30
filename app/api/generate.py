from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..core.security import security, decode_token
from ..core.database import supabase
from ..models.schemas import ComponentCreate, Component
from ..core.code_generator import create_generation_workflow
from datetime import datetime
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

router = APIRouter()

async def get_current_user_id(token: str = Depends(security)):
    payload = decode_token(token.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return int(payload.get("sub"))

@router.post("/")
async def generate_code(
    prompt: str,
    framework: str,
    current_user_id: int = Depends(get_current_user_id)
):
    # Create and run the generation workflow
    workflow = create_generation_workflow()
    
    # Run the workflow
    result = workflow.invoke({
        "prompt": prompt,
        "framework": framework
    })
    
    # Extract generated components
    components = result["generated_components"]
    
    # Combine all component codes into a single string
    all_imports = set()
    all_styles = []
    all_components = []
    
    for component in components:
        all_imports.update(component["imports"])
        if component["styles"]:
            all_styles.append(component["styles"])
        all_components.append(component["code"])
    
    # Combine everything into a single code string
    generated_code = "\n".join([
        "// Imports",
        "\n".join(all_imports),
        "\n// Styles",
        "\n".join(all_styles),
        "\n// Components",
        "\n".join(all_components)
    ])
    
    # Store components in database
    for component in components:
        new_component = {
            "name": component["name"],
            "code": component["code"],
            "type": component["type"],
            "created_at": datetime.utcnow()
        }
        supabase.table("components").insert(new_component).execute()

    return {
        "code": generated_code,
        "components": components
    }

@router.post("/validate")
async def validate_code(
    code: str,
    current_user_id: int = Depends(get_current_user_id)
):
    messages = [
        SystemMessage(content="You are a code validator. Check the following code for errors and best practices."),
        HumanMessage(content=f"""
        Validate the following code:
        
        ```
        {code}
        ```
        
        Return the response as valid JSON with the following structure:
        {{
            "valid": boolean,
            "errors": ["error messages"],
            "warnings": ["warning messages"],
            "suggestions": ["improvement suggestions"]
        }}
        """)
    ]
    
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke(messages)
    
    try:
        result = json.loads(response.content)
        return result
    except:
        return {
            "valid": False,
            "errors": ["Failed to validate code"],
            "warnings": [],
            "suggestions": []
        }

@router.post("/components", response_model=Component)
async def create_component(
    component: ComponentCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    # First verify that the project belongs to the user
    project = supabase.table("projects").select("*").eq("id", component.project_id).execute()
    
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.data[0]["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add components to this project")
    
    result = supabase.table("components").insert(component.dict()).execute()
    return result.data[0]

@router.get("/components/{project_id}", response_model=List[Component])
async def get_project_components(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    # Verify project ownership
    project = supabase.table("projects").select("*").eq("id", project_id).execute()
    
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.data[0]["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these components")
    
    result = supabase.table("components").select("*").eq("project_id", project_id).execute()
    return result.data 