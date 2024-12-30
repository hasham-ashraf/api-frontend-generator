from supabase import create_client
from ..config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Create tables
def init_db():
    # Users table
    supabase.table("users").create({
        "id": "int8",
        "email": "varchar",
        "password_hash": "varchar",
        "is_verified": "bool",
        "created_at": "timestamptz",
        "updated_at": "timestamptz"
    }, primary_key="id")

    # Projects table
    supabase.table("projects").create({
        "id": "int8",
        "user_id": "int8",
        "name": "varchar",
        "description": "text",
        "prompt": "text",
        "generated_code": "text",
        "framework": "varchar",
        "created_at": "timestamptz",
        "updated_at": "timestamptz"
    }, primary_key="id")

    # Components table
    supabase.table("components").create({
        "id": "int8",
        "project_id": "int8",
        "name": "varchar",
        "code": "text",
        "type": "varchar",
        "created_at": "timestamptz"
    }, primary_key="id") 