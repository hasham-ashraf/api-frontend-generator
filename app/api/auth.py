from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from datetime import timedelta
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    security
)
from ..core.database import supabase
from ..models.schemas import UserCreate, Token, User
from ..config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    user = supabase.table("users").select("*").eq("email", user_data.email).execute()
    if user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "email": user_data.email,
        "password_hash": hashed_password,
        "is_verified": False
    }
    
    result = supabase.table("users").insert(new_user).execute()
    user_id = result.data[0]["id"]
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_data: UserCreate):
    # Get user
    user = supabase.table("users").select("*").eq("email", user_data.email).execute()
    if not user.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = user.data[0]
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 