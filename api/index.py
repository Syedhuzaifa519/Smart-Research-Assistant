from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

from agent.llm import LLMClient
from agent.core import ResearchAgent
from tools.base import ToolRegistry
from tools.search import SearchTool
from tools.extract import ExtractTool

app = FastAPI(title="Smart Research Assistant API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    topic: str
    report: str
    usage: dict

@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    try:
        # 1. Initialize Registry and Tools
        registry = ToolRegistry()
        registry.register_tool(SearchTool())
        registry.register_tool(ExtractTool())

        # 2. Initialize LLM and Agent
        llm_client = LLMClient()
        agent = ResearchAgent(llm_client, registry)

        # 3. Run Research
        report_data = agent.run(request.topic)
        
        # Extract the final Markdown text from the agent's messages
        final_message = agent.messages[-1]["content"]
        final_text = ""
        for block in final_message:
            if block.type == "text":
                final_text += block.text
        
        return {
            "topic": request.topic,
            "report": final_text,
            "usage": llm_client.get_usage_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
