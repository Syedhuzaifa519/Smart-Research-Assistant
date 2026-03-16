from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    """Represents a single result from a web search."""
    title: str
    url: str
    snippet: str
    relevance_score: float = 0.0

class ResearchFinding(BaseModel):
    """A specific claim or piece of information found during research."""
    claim: str
    source_url: str
    source_title: str
    confidence: float = Field(ge=0.0, le=1.0)

class ToolCall(BaseModel):
    """Details of a tool execution by the agent."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    duration_ms: float

class AgentStep(BaseModel):
    """A single iteration of the ReAct loop."""
    step_number: int
    thought: str
    action: Optional[ToolCall] = None
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ResearchReport(BaseModel):
    """The final synthesized research report."""
    topic: str
    summary: str
    findings: List[ResearchFinding]
    sources: List[Dict[str, str]]  # list of {'title': ..., 'url': ...}
    contradictions: List[str] = []
    agent_steps: List[AgentStep] = []
    created_at: datetime = Field(default_factory=datetime.now)
