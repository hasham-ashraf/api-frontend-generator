from fastapi import FastAPI
from app.api.endpoints import auth, projects, agents, components

app = FastAPI(title="AI Frontend Generator API")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(components.router, prefix="/api/v1/components", tags=["components"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 