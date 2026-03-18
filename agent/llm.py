import time
import logging
import os
from typing import List, Dict, Any, Optional
import openai
from agent.config import MODEL_NAME, MAX_TOKENS

logger = logging.getLogger(__name__)

class LLMClient:
    """
    A thin wrapper around the OpenAI/Deepseek API client.
    Handles retries, logging, and token usage tracking.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("deepseak_API_KEY")
        if not self.api_key:
            raise ValueError("API key is missing. Please set it in your .env file.")
        
        # DeepSeek uses an OpenAI compatible API structure usually
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com/beta" # Use DeepSeek base URL if needed, or openai default
        )
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def chat(self, 
             messages: List[Dict[str, Any]], 
             system_prompt: str, 
             tools: Optional[List[Dict[str, Any]]] = None,
             max_retries: int = 3) -> Any:
        """
        Sends a request to the LLM with exponential backoff on failure.
        """
        # Ensure system prompt is in messages
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                kwargs = {
                    "model": MODEL_NAME or "deepseek-chat",
                    "max_tokens": MAX_TOKENS,
                    "messages": all_messages,
                }
                
                if tools:
                    kwargs["tools"] = tools

                response = self.client.chat.completions.create(**kwargs)
                
                # Track token usage
                if hasattr(response, 'usage') and response.usage:
                    self.total_input_tokens += getattr(response.usage, 'prompt_tokens', 0)
                    self.total_output_tokens += getattr(response.usage, 'completion_tokens', 0)
                
                latency = (time.time() - start_time) * 1000
                in_tokens = getattr(response.usage, 'prompt_tokens', 0) if response.usage else 0
                out_tokens = getattr(response.usage, 'completion_tokens', 0) if response.usage else 0
                logger.debug(f"LLM Call latency: {latency:.2f}ms | Tokens: In={in_tokens}, Out={out_tokens}")
                
                return response

            except openai.APIConnectionError as e:
                logger.warning(f"Connection error to API (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1: raise
                time.sleep(2 ** attempt)  # Exponential backoff
            except openai.RateLimitError as e:
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
