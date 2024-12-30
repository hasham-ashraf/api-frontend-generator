from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..core.security import security, decode_token
from ..core.database import supabase
from ..models.schemas import ProjectCreate, Project
from datetime import datetime

router = APIRouter()

async def get_current_user_id(token: str = Depends(security)):
    payload = decode_token(token.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return int(payload.get("sub"))

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    new_project = {
        **project.dict(),
        "user_id": current_user_id,
        "generated_code": "",  # Will be populated after generation
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = supabase.table("projects").insert(new_project).execute()
    return result.data[0]

@router.get("/", response_model=List[Project])
async def get_projects(current_user_id: int = Depends(get_current_user_id)):
    result = supabase.table("projects").select("*").eq("user_id", current_user_id).execute()
    return result.data

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    result = supabase.table("projects").select("*").eq("id", project_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = result.data[0]
    if project["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_update: ProjectCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    # Check if project exists and belongs to user
    existing = supabase.table("projects").select("*").eq("id", project_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if existing.data[0]["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this project")
    
    update_data = {
        **project_update.dict(),
        "updated_at": datetime.utcnow()
    }
    
    result = supabase.table("projects").update(update_data).eq("id", project_id).execute()
    return result.data[0]

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    # Check if project exists and belongs to user
    existing = supabase.table("projects").select("*").eq("id", project_id).execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if existing.data[0]["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    supabase.table("projects").delete().eq("id", project_id).execute()
    return {"success": True} 