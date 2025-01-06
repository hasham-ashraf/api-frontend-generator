from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any

# Load environment variables
load_dotenv()

# Verify required environment variables
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

from .models import GenerationRequest
from .utils.sse import format_sse_event
from .agents.prompt_analyzer import prompt_analyzer
from .agents.architecture_designer import architecture_designer
from .agents.react_generator import react_generator

# Define the state schema
class AgentStateDict(TypedDict):
    prompt: str
    requirements: List[str]
    components: List[str]
    files: Dict[str, str]
    current_stage: str

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create LangGraph workflow
workflow = StateGraph(AgentStateDict)

# Add nodes
workflow.add_node("analyze", prompt_analyzer)
workflow.add_node("design", architecture_designer)
workflow.add_node("generate", react_generator)

# Define edges
workflow.add_edge("analyze", "design")
workflow.add_edge("design", "generate")
workflow.add_edge("generate", END)

# Set the entry point
workflow.set_entry_point("analyze")

# Compile graph
chain = workflow.compile()

@app.post("/generate")
async def generate_code(request: GenerationRequest):
    async def generate():
        # Initialize state
        state = {
            "prompt": request.prompt,
            "requirements": [],
            "components": [],
            "files": {},
            "current_stage": "init"
        }
        
        # Run graph with streaming
        async for update in chain.astream(state):
            if "generate" in update or "__end__" in update:
                if "__end__" in update:
                    files = update["__end__"]["files"]
                else:
                    files = update["generate"]["files"]

                print("Generator agent")
                
                yield format_sse_event(
                    files
                )

            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 