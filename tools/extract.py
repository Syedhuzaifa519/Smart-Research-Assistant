import httpx
from typing import Any, Dict
from tools.base import Tool

class ExtractTool(Tool):
    """
    Tool for extracting content from a specific URL.
    Useful for reading detailed information when snippets are insufficient.
    """

    @property
    def name(self) -> str:
        return "extract_content"

    @property
    def description(self) -> str:
        return (
            "Fetch and extract the main text content from a specific URL. "
            "Use this when a search snippet doesn't provide enough detail "
            "to understand a source's claims."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to extract content from."
                }
            },
            "required": ["url"]
        }

    def execute(self, url: str) -> Dict[str, Any]:
        try:
            # We'll use a simple approach here. For production, consider 
            # something like 'trafilatura' or 'readability-lxml'.
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                
                # Mock extraction (just getting raw text for now)
                # In a real scenario, we'd strip HTML tags carefully.
                text = response.text
                
                # Simple truncation to avoid token bloat
                max_chars = 6000
                content = text[:max_chars] + "..." if len(text) > max_chars else text
                
                return {
                    "url": url,
                    "content": content,
                    "length": len(content)
                }
        except Exception as e:
            return {"error": f"Failed to extract content from {url}: {str(e)}"}
