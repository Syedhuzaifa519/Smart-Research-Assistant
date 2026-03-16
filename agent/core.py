import json
import logging
import time
from typing import List, Optional

from agent.llm import LLMClient
from agent.prompts import SYSTEM_PROMPT, RESEARCH_QUERY_TEMPLATE
from agent.config import MAX_ITERATIONS
from tools.base import ToolRegistry
from models.schemas import ResearchReport, AgentStep, ToolCall

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    The core agent class that manages the ReAct loop.
    """
    
    def __init__(self, llm_client: LLMClient, tool_registry: ToolRegistry):
        self.llm = llm_client
        self.tools = tool_registry
        self.messages = []

    def run(self, topic: str) -> ResearchReport:
        """
        Runs the research process for a given topic.
        """
        logger.info(f"Starting research on: {topic}")
        
        user_message = RESEARCH_QUERY_TEMPLATE.format(topic=topic)
        self.messages = [{"role": "user", "content": user_message}]
        
        agent_steps = []
        
        for i in range(MAX_ITERATIONS):
            logger.info(f"Iteration {i+1}/{MAX_ITERATIONS}")
            
            # 1. Call LLM
            response = self.llm.chat(
                messages=self.messages,
                system_prompt=SYSTEM_PROMPT,
                tools=self.tools.get_tool_schemas()
            )
            
            # Add assistant message to history
            self.messages.append({"role": "assistant", "content": response.content})
            
            # Process response content blocks
            tool_calls_in_this_step = []
            final_text = ""
            
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
                elif block.type == "tool_use":
                    # 2. Execute Tool
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id
                    
                    start_time = time.time()
                    try:
                        result = self.tools.execute(tool_name, **tool_input)
                        duration = (time.time() - start_time) * 1000
                        
                        # Store tool call info
                        tool_call = ToolCall(
                            tool_name=tool_name,
                            arguments=tool_input,
                            result=result,
                            duration_ms=duration
                        )
                        tool_calls_in_this_step.append(tool_call)
                        
                        # 3. Add Tool Result to history
                        self.messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(result)
                            }]
                        })
                        
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {e}")
                        # Inform the agent about the error
                        self.messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps({"error": str(e)}),
                                "is_error": True
                            }]
                        })

            # Record this step
            # Note: We're assuming the text block contains the "Thought"
            step = AgentStep(
                step_number=i + 1,
                thought=final_text.strip(),
                action=tool_calls_in_this_step[0] if tool_calls_in_this_step else None,
                observation=json.dumps(tool_calls_in_this_step[0].result) if tool_calls_in_this_step else None
            )
            agent_steps.append(step)

            # Check if LLM is done (returned text but no tool calls)
            if not tool_calls_in_this_step and final_text:
                logger.info("Agent has finished research.")
                # Return report (we'll parse it better later, but for now wrap the text)
                return ResearchReport(
                    topic=topic,
                    summary="Full report generated",
                    findings=[], # Would need deeper parsing for structure
                    sources=[],
                    agent_steps=agent_steps
                )

        raise RuntimeError(f"Agent exceeded maximum iterations ({MAX_ITERATIONS}) without finishing.")
