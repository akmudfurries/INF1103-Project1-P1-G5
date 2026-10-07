# config.py
import os

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

# values required by business_rules.py
BUSINESS_AI_VALUES = {
    "demand_level": {"low", "medium", "high"},
    "demand_trend": {"stable", "increasing", "decreasing"},
    "stock_condition": {"healthy", "at_risk", "critical"},
    "stockout_risk": {"low", "medium", "high"},
    "supply_risk": {"low", "medium", "high"},
}

# Allowed answers for each question
ALLOWED_ANSWERS = { 
    "demand_level": ["low", "medium", "high"],
    "demand_trend": ["decreasing", "stable", "increasing"],
    "supplier_issue": ["none", "potential", "significant"],
    "operational_importance": ["low", "medium", "high"],
 }

MAX_RETRIES = 3 # Max retries by AI before giving up, Total 4 attempts