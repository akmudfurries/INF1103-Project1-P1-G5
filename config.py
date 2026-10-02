# config.py
import os

# --- APP IDENTIFICATION ---
APP_TITLE = "AI INVENTORY & PROCUREMENT ADVISOR"

# --- PERSISTENCE PATHS ---
DATA_DIR = "data"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.json")
DECISIONS_FILE = os.path.join(DATA_DIR, "procurement_decisions.json")

# --- ACCEPTED ENUMS FOR VALIDATION ---
# Predefined categories to validate AI response fields against
ACCEPTED_DEMAND_LEVELS = ["low", "medium", "high"]
ACCEPTED_DEMAND_TRENDS = ["decreasing", "stable", "increasing"]
ACCEPTED_STOCK_CONDITIONS = ["optimal", "adequate", "at_risk", "critical"]
ACCEPTED_RISK_LEVELS = ["low", "medium", "high"]

# Allowed answers for each question
ALLOWED_ANSWERS = { 
    "demand_level": ["low", "medium", "high"],
    "demand_trend": ["decreasing", "stable", "increasing"],
    "supplier_issue": ["none", "potential", "significant"],
    "operational_importance": ["low", "medium", "high"],
 }
MAX_RETRIES = 3 # Max retries by AI before giving up, Total 4 attempts 
>>>>>>> 347cd5de7c75eb3ff8bbb0b57017b5b835763f25
