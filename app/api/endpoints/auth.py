from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from app.db.client import get_db
from typing import Optional
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password
)
from uuid import UUID
import json

router = APIRouter()
security = HTTPBearer()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    email: str
    name: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str

@router.post("/register", response_model=TokenResponse)
async def register(user: UserCreate):
    db = await get_db()
    try:
        # Check if user exists
        existing_user = db.table('users').select("*").eq('email', user.email).execute()
        if existing_user.data and len(existing_user.data) > 0:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user with hashed password
        password_hash = get_password_hash(user.password)
        new_user = {
            "email": user.email,
            "password_hash": password_hash,
            "name": user.name,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = db.table('users').insert(new_user).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=400, detail="Failed to create user")
            
        created_user = result.data[0]
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(created_user["id"]),
                "email": created_user["email"]
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=created_user["id"],
            email=created_user["email"],
            name=created_user["name"]
        )
    except Exception as e:
        # Better error handling
        error_msg = str(e)
        try:
            # Try to parse error message if it's JSON
            error_detail = json.loads(error_msg)
            if isinstance(error_detail, dict) and 'message' in error_detail:
                error_msg = error_detail['message']
        except:
            pass
        raise HTTPException(status_code=400, detail=error_msg)

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    db = await get_db()
    try:
        # Get user by email
        result = db.table('users').select("*").eq('email', user.email).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = result.data[0]
        
        # Verify password
        if not verify_password(user.password, db_user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Update last login
        db.table('users').update({
            "last_login": datetime.utcnow().isoformat()
        }).eq('id', db_user["id"]).execute()
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(db_user["id"]),
                "email": db_user["email"]
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=db_user["id"],
            email=db_user["email"],
            name=db_user["name"]
        )
    except Exception as e:
        error_msg = "Invalid credentials"
        if not isinstance(e, HTTPException):
            print(f"Login error: {str(e)}")  # Log the actual error
        raise HTTPException(status_code=401, detail=error_msg)

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: dict = Depends(verify_token)):
    db = await get_db()
    try:
        user_id = token["sub"]
        result = db.table('users').select("id, email, name").eq('id', user_id).execute()
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") 