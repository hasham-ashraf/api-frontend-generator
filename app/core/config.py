from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "AI Frontend Generator"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Supabase Settings
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # OpenAI Settings
    OPENAI_API_KEY: str
    
    # JWT Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

OPENAI_CONFIG = {
    'requirements': {
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.7,
        'max_tokens': 4000
    },
    'design': {
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.4,
        'max_tokens': 4000
    },
    'code': {
        'model': 'gpt-3.5-turbo-0125',
        'temperature': 0.2,
        'max_tokens': 4000
    }
}

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 