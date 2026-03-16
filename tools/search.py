from typing import Any, Dict, List
from tavily import TavilyClient
from tools.base import Tool
from agent.config import TAVILY_API_KEY
from models.schemas import SearchResult

class SearchTool(Tool):
    """
    Tool for searching the web using the Tavily API.
    Returns high-quality, research-oriented results.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or TAVILY_API_KEY
        if not self.api_key:
            self._client = None
        else:
            self._client = TavilyClient(api_key=self.api_key)

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for current information on a topic. "
            "Use this when you need facts, recent events, or to verify claims. "
            "The query should be specific. Returns a list of results with titles, "
            "URLs, and snippets."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The specific search query."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-10).",
                    "default": 5
                }
            },
            "required": ["query"]
        }

    def execute(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self._client:
            return [{"error": "Tavily API key is missing. Cannot perform search."}]
        
        try:
            response = self._client.search(query=query, max_results=max_results, search_depth="advanced")
            
            results = []
            for res in response.get("results", []):
                results.append({
                    "title": res.get("title"),
                    "url": res.get("url"),
                    "snippet": res.get("content") or res.get("snippet", ""),
                    "score": res.get("score", 0.0)
                })
            return results
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
