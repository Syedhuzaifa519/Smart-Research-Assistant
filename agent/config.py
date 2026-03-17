import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).parent.parent

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "claude-3-5-sonnet-20240620")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
MAX_TOKENS = 4096

# Output Directory
OUTPUT_DIR = BASE_DIR / "output"
# OUTPUT_DIR.mkdir(exist_ok=True)
import os

# Pehle sirf ye line thi:
# OUTPUT_DIR.mkdir(exist_ok=True) <-- Ye crash kar rahi thi

# Ab humne ye kar diya:
if not os.environ.get("VERCEL"):
    OUTPUT_DIR.mkdir(exist_ok=True)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
