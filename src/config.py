from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "claude-haiku-4-5-20251001")
MAX_HISTORY_TURNS: int = int(os.environ.get("MAX_HISTORY_TURNS", "5"))
MAX_COST_USD: float = float(os.environ.get("MAX_COST_USD", "1.0"))

# Pricing per million tokens for claude-haiku-4-5
INPUT_COST_PER_MTOK: float = 0.80
OUTPUT_COST_PER_MTOK: float = 4.00

# Default player starting values (Hebrew)
DEFAULT_PLAYER_CLASS: str = "לוחם"
DEFAULT_STARTING_LOCATION: str = "כפר ראשית"
DEFAULT_MAX_HEALTH: int = 100
