from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Frontend Generator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings() 