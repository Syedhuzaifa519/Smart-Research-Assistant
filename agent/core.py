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
            assistant_message = response.choices[0].message
            self.messages.append(assistant_message.model_dump(exclude_unset=True))
            
            # Process response content
            tool_calls_in_this_step = []
            final_text = assistant_message.content or ""
            
            tool_calls = assistant_message.tool_calls
            if tool_calls:
                for tool_call_obj in tool_calls:
                    # 2. Execute Tool
                    tool_name = tool_call_obj.function.name
                    tool_input = json.loads(tool_call_obj.function.arguments)
                    tool_use_id = tool_call_obj.id
                    
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
                            "role": "tool",
                            "tool_call_id": tool_use_id,
                            "content": json.dumps(result)
                        })
                        
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {e}")
                        # Inform the agent about the error
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_use_id,
                            "content": json.dumps({"error": str(e)})
                        })

            # Record this step
            step = AgentStep(
                step_number=i + 1,
                thought=final_text.strip() if final_text else "",
                action=tool_calls_in_this_step[0] if tool_calls_in_this_step else None,
                observation=json.dumps(tool_calls_in_this_step[0].result) if tool_calls_in_this_step else None
            )
            agent_steps.append(step)

            # Check if LLM is done (returned text but no tool calls)
            if not tool_calls and final_text:
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
