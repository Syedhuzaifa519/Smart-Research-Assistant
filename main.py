import sys
import logging
import argparse
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.markdown import Markdown

from agent.config import LOG_LEVEL
from agent.llm import LLMClient
from agent.core import ResearchAgent
from tools.base import ToolRegistry
from tools.search import SearchTool
from tools.extract import ExtractTool

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("smart-research-assistant")
console = Console()

def main():
    parser = argparse.ArgumentParser(description="Smart Research Assistant Agent")
    parser.add_argument("topic", type=str, nargs="?", help="The topic you want to research")
    args = parser.parse_args()

    topic = args.topic
    if not topic:
        console.print("[bold cyan]Welcome to the Smart Research Assistant![/bold cyan]")
        topic = console.input("[bold blue]What topic would you like me to research? [/bold blue]")

    # 1. Initialize Registry and Tools
    registry = ToolRegistry()
    registry.register_tool(SearchTool())
    registry.register_tool(ExtractTool())

    # 2. Initialize LLM and Agent
    try:
        llm_client = LLMClient()
        agent = ResearchAgent(llm_client, registry)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize agent: {e}[/bold red]")
        sys.exit(1)

    # 3. Run Research
    console.print(Panel(f"Starting research on: [bold green]{topic}[/bold green]", expand=False))
    
    with console.status("[bold yellow]Agent is thinking and searching...", spinner="dots"):
        try:
            report = agent.run(topic)
        except Exception as e:
            console.print(f"[bold red]Research failed: {e}[/bold red]")
            sys.exit(1)

    # 4. Display Final Output
    # The agent.run returns text content in messages history usually as the last assistant message
    final_message = agent.messages[-1]["content"]
    final_text = ""
    for block in final_message:
        if block.type == "text":
            final_text += block.text

    console.print("\n")
    console.print(Panel("Research Report Compleated", style="bold green"))
    console.print(Markdown(final_text))

    # 5. Usage Statistics
    stats = llm_client.get_usage_stats()
    console.print("\n[dim]Usage Stats:[/dim]")
    console.print(f"[dim]Total Tokens: {stats['total_tokens']} (In: {stats['input_tokens']}, Out: {stats['output_tokens']})[/dim]")
    
    # Save to file
    filename = f"output/research_{topic.lower().replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(final_text)
    console.print(f"\n[bold blue]Report saved to: {filename}[/bold blue]")

if __name__ == "__main__":
    main()
