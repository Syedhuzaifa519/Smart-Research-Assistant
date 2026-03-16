import time
import logging
from typing import List, Dict, Any, Optional
import anthropic
from agent.config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS

logger = logging.getLogger(__name__)

class LLMClient:
    """
    A thin wrapper around the Anthropic API client.
    Handles retries, logging, and token usage tracking.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("Anthropic API key is missing. Please set it in your .env file.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def chat(self, 
             messages: List[Dict[str, Any]], 
             system_prompt: str, 
             tools: Optional[List[Dict[str, Any]]] = None,
             max_retries: int = 3) -> anthropic.types.Message:
        """
        Sends a request to the LLM with exponential backoff on failure.
        """
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                kwargs = {
                    "model": MODEL_NAME,
                    "max_tokens": MAX_TOKENS,
                    "system": system_prompt,
                    "messages": messages,
                }
                
                if tools:
                    kwargs["tools"] = tools

                response = self.client.messages.create(**kwargs)
                
                # Track token usage
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens
                
                latency = (time.time() - start_time) * 1000
                logger.debug(f"LLM Call latency: {latency:.2f}ms | Tokens: In={response.usage.input_tokens}, Out={response.usage.output_tokens}")
                
                return response

            except anthropic.APIConnectionError as e:
                logger.warning(f"Connection error to Anthropic API (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1: raise
                time.sleep(2 ** attempt)  # Exponential backoff
            except anthropic.RateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1: raise
                time.sleep(5 ** attempt)  # Longer backoff for rate limits
            except Exception as e:
                logger.error(f"Unexpected error in LLM call: {e}")
                raise

    def get_usage_stats(self) -> Dict[str, int]:
        """Returns the total token usage for this client instance."""
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }
