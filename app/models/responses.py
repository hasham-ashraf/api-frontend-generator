from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentResponse(BaseModel):
    status: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] 