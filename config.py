# config.py
import os

# --- APP IDENTIFICATION ---
APP_TITLE = "AI INVENTORY & PROCUREMENT ADVISOR"
APP_SUBTITLE = "Operational Insight & Procurement Engine"
LINE_WIDTH = 50
BANNER_CHAR = "="
DIVIDER_CHAR = "-"
MAX_RETRIES = 3

# --- PERSISTENCE PATHS ---
DATA_DIR = "data"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
DECISIONS_FILE = os.path.join(DATA_DIR, "procurement_decisions.json")

# values required by business_rules.py
BUSINESS_AI_VALUES = {
    "demand_level": {"low", "medium", "high"},
    "demand_trend": {"stable", "increasing", "decreasing"},
    "supply_risk": {"low", "medium", "high"},
    "operational_importance": {"low", "medium", "high"},
}

# Allowed answers for each question
ALLOWED_ANSWERS = { 
    "demand_level": ["low", "medium", "high"],
    "demand_trend": ["stable", "increasing", "decreasing"],
    "supply_risk": ["low", "medium", "high"],
    "operational_importance": ["low", "medium", "high"],
 }