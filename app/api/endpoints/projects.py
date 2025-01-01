from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.db.client import get_db
from app.core.security import verify_token

router = APIRouter()
security = HTTPBearer()

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: dict = {}

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

@router.get("/", response_model=List[Project])
async def list_projects(token: dict = Depends(verify_token)):
    db = await get_db()
    try:
        user_id = token["sub"]
        projects = db.table('projects').select("*").eq('user_id', user_id).execute()
        return projects.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    token: dict = Depends(verify_token)
):
    db = await get_db()
    try:
        user_id = token["sub"]
        now = datetime.utcnow().isoformat()
        new_project = {
            "name": project.name,
            "description": project.description,
            "config": project.config,
            "user_id": user_id,
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        
        result = db.table('projects').insert(new_project).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=400, detail="Failed to create project")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    token: dict = Depends(verify_token)
):
    db = await get_db()
    try:
        user_id = token["sub"]
        result = db.table('projects').select("*").eq('id', project_id).eq('user_id', user_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Project not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    token: dict = Depends(verify_token)
):
    db = await get_db()
    try:
        user_id = token["sub"]
        
        # Check if project exists and belongs to user
        existing = db.table('projects').select("*").eq('id', project_id).eq('user_id', user_id).execute()
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        update_data = {
            "name": project.name,
            "description": project.description,
            "config": project.config,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = db.table('projects').update(update_data).eq('id', project_id).eq('user_id', user_id).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    token: dict = Depends(verify_token)
):
    db = await get_db()
    try:
        user_id = token["sub"]
        
        # Check if project exists and belongs to user
        existing = db.table('projects').select("*").eq('id', project_id).eq('user_id', user_id).execute()
        if not existing.data or len(existing.data) == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        result = db.table('projects').delete().eq('id', project_id).eq('user_id', user_id).execute()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 