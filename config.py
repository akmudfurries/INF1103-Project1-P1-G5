# config.py
import os

TIMEZONE = "Asia/Singapore"

# AI settings
MAX_RETRIES = 3
GEMINI_MODEL = "gemini-3.1-flash-lite"
AI_TIMEOUT_MS = 30000

# --- APP IDENTIFICATION ---
APP_TITLE = "AI INVENTORY & PROCUREMENT ADVISOR"
APP_SUBTITLE = "Operational Insight & Procurement Engine"
LINE_WIDTH = 50
BANNER_CHAR = "="
DIVIDER_CHAR = "-"

# --- PERSISTENCE PATHS ---
DATA_DIR = "data"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
DECISIONS_FILE = os.path.join(DATA_DIR, "procurement_decisions.json")


# --- Allowed Ans For Ai And Business Rules ---
ALLOWED_ANSWERS = { 
    "demand_level": ["low", "medium", "high"],
    "demand_trend": ["stable", "increasing", "decreasing"],
    "supply_risk": ["low", "medium", "high"],
    "operational_importance": ["low", "medium", "high"],
 }