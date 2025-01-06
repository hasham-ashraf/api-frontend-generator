from pydantic import BaseModel
from typing import List, Dict, Any

class GenerationRequest(BaseModel):
    prompt: str

class FileContent(BaseModel):
    path: str
    content: str
    type: str

class GenerationResponse(BaseModel):
    files: List[FileContent]
    metadata: Dict[str, Any] 