from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    framework: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    user_id: int
    generated_code: str
    created_at: datetime
    updated_at: datetime

class ComponentBase(BaseModel):
    name: str
    code: str
    type: str

class ComponentCreate(ComponentBase):
    project_id: int

class Component(ComponentBase):
    id: int
    created_at: datetime 