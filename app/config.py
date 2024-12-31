from typing import Optional
import os

class Settings:
    PROJECT_NAME: str = "Frontend Generator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3000

settings = Settings() 