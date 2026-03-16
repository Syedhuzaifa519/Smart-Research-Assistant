# Smart Research Assistant

A professional, agentic AI research assistant built from scratch using the ReAct (Reason + Act) pattern. This agent autonomously plans its research, searches the web, extracts information, and synthesizes comprehensive reports with citations.

## 🚀 Key Features
- **Raw ReAct Loop**: No agent frameworks used—built with pure Python and Anthropic's tool-calling API.
- **Autonomous Research**: The agent decides when to search, what to extract, and when to stop.
- **Evidence-Based**: Every claim includes source citations and URLs.
- **Polished CLI**: Beautiful terminal output powered by `rich`.

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Syedhuzaifa519/Smart-Research-Assistant.git
cd Smart-Research-Assistant

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

1. Create a `.env` file in the root directory:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 📖 Usage

Run the researcher from your terminal:

```bash
python main.py "Future of quantum computing in 2025"
```

## 🏗️ Project Structure
- `agent/`: Core ReAct logic and LLM client.
- `tools/`: Web search and extraction tools.
- `models/`: Data validation schemas (Pydantic).
- `output/`: Generated research reports.
