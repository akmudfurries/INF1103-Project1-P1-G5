import config
import validation


def print_header(): # display top app title banner
    print(config.BANNER_CHAR * config.LINE_WIDTH)
    print(f"{config.APP_TITLE.center(config.LINE_WIDTH)}")
    print(f"{config.APP_SUBTITLE.center(config.LINE_WIDTH)}")
    print(config.BANNER_CHAR * config.LINE_WIDTH)

def get_main_menu_choice(): # renders main CLI menu with quit and captures user choice
    print("\n [ MAIN MENU ]")
    print("1. Add new inventory record")
    print("2. View stored inventory records")
    print("3. Run inventory analysis")
    print("4. View previous procurement recommendations")
    print("5. Exit")
    return input("\nSelect an option (1-5), or 'q' to quit: ").strip().lower()

def _get_input_or_cancel(prompt_text):
    # helper to catch 'q' or 'quit' at any prompt.
    val = input(prompt_text).strip()
    if val.lower() in ['q', 'quit']:
        print("\n[!] Operation cancelled by user.")
        return None
    return val

def prompt_inventory_record(): # collects raw inventory item input fields
    print("\n" + config.DIVIDER_CHAR * config.LINE_WIDTH)
    print(" CREATE NEW INVENTORY RECORD (Type 'q' to cancel) ")
    print(config.DIVIDER_CHAR * config.LINE_WIDTH)

    item = _get_input_or_cancel("Item Name / ID: ")
    if item is None: return None

    category = _get_input_or_cancel("Category: ")
    if category is None: return None

    stock_raw = _get_input_or_cancel("Current Stock (units): ")
    if stock_raw is None: return None

    usage_raw = _get_input_or_cancel("Average Weekly Usage (units): ")
    if usage_raw is None: return None

    lead_raw = _get_input_or_cancel("Supplier Lead Time (weeks): ")
    if lead_raw is None: return None

    moq_raw = _get_input_or_cancel("Minimum Order Quantity (units): ")
    if moq_raw is None: return None

    cost_raw = _get_input_or_cancel("Unit Cost ($): ")
    if cost_raw is None: return None

    budget_raw = _get_input_or_cancel("Available Budget ($): ")
    if budget_raw is None: return None

    notes = _get_input_or_cancel("Operational Notes: ")
    if notes is None: return None

    # validate inputs using validation.py
    is_valid, errors, parsed = validation.validate_inventory_fields(
        item, category, stock_raw, usage_raw, lead_raw, moq_raw, cost_raw, budget_raw, notes
    )

    if not is_valid:
        print("\n[!] Input Validation Failed:")
        for err in errors:
            print(f"  - {err}")
        print("[!] Record creation aborted. Please try again.")
        return None

# mapped keys matching team schema
    return { 
        "item_id": item,
        "item_name": item,
        "category": category,
        "current_stock": parsed["Current Stock"],
        "weekly_usage": parsed["Average Weekly Usage"],
        "lead_time_weeks": parsed["Supplier Lead Time"],
        "moq": parsed["Minimum Order Quantity"],
        "unit_cost": parsed["Unit Cost"],
        "budget": parsed["Available Budget"],
        "operational_notes": notes
    }

def display_inventory_records(records): # displays saved inventory records
    if not records:
        print("\nNo inventory records found.")
        return

    print("\n--- STORED INVENTORY RECORDS ---")
    for idx, item in enumerate(records, start=1):
        name = item.get("item_name") or item.get("item", "Unknown Item")
        cat = item.get("category", "General")
        stock = item.get("current_stock", 0)
        print(f"[{idx}] {name} | Category: {cat} | Stock: {stock} units")

def display_full_procurement_report(inventory, ai_assessment, analysis_result): # renders complete analysis output and metrics
    print("\n" + config.BANNER_CHAR * config.LINE_WIDTH)
    print(f"{config.APP_TITLE:^{config.LINE_WIDTH}}")
    print(config.BANNER_CHAR * config.LINE_WIDTH)

    item_name = inventory.get('item_name') or inventory.get('item', 'N/A')
    category = inventory.get('category', 'General')
    print(f"Item Name: {item_name} ({category})")

    # quantitative inventory data
    print("\n[Inventory Data]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Current Stock:      {inventory.get('current_stock', 0)} units")
    print(f"Weekly Usage:       {inventory.get('weekly_usage', 0.0)} units")
    print(f"Supplier Lead Time: {inventory.get('lead_time_weeks', 0)} weeks")

    coverage = analysis_result.get('stock_coverage')
    coverage_str = f"{coverage:.1f} weeks" if coverage is not None else "N/A"
    print(f"Stock Coverage:     {coverage_str}")

    # ai assessment (ref to ai_manager.py  / business_rules.py)
    print("\n[AI Assessment]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Demand Level:           {ai_assessment.get('demand_level', 'N/A').upper()}")
    print(f"Demand Trend:           {ai_assessment.get('demand_trend', 'N/A').upper()}")
    print(f"Supply Risk:            {ai_assessment.get('supply_risk', 'N/A').upper()}")
    print(f"Operational Importance: {ai_assessment.get('operational_importance', 'N/A').upper()}")
    print(f"Reason:                 {ai_assessment.get('reason', 'N/A')}")

    # procurement analysis calculations (ref to business_rules.py)
    print("\n[Procurement Analysis]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Recommended Order:  {analysis_result.get('recommended_quantity', 0)} units")

    # Extended metrics conditional filter
    if "reorder_point" in analysis_result:
        print(f"Reorder Point:      {analysis_result['reorder_point']} units")

    if "estimated_cost" in analysis_result:
        print(f"Estimated Cost:     ${analysis_result['estimated_cost']:.2f}")

    if "budget" in analysis_result:
        print(f"Available Budget:   ${analysis_result['budget']:.2f}")

    # decision output and priority
    print("\n[Final Decision]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Priority:           {analysis_result.get('priority', 'NORMAL')}")
    print(f"Action:             {analysis_result.get('action', 'NO ACTION')}")

    if "budget_escalation" in analysis_result:
        escalation = "REQUIRED" if analysis_result.get('budget_escalation') else "NOT REQUIRED"
        print(f"Budget Escalation:  {escalation}")
    

    print(config.BANNER_CHAR * config.LINE_WIDTH)

def prompt_user_approval(): # prompts user to approve or reject the generated procurement decision or quit
    while True:
        choice = input("\nDo you APPROVE this recommendation? (Y/N/Quit): ").strip().upper()
        if choice in ['Y', 'YES']:
            print("\n[STATUS] Procurement recommendation APPROVED.")
            return "APPROVED", ""
        elif choice in ['N', 'NO']:
            reason = input("Enter reason for rejection/overriding decision: ").strip()
            print(f"\n[STATUS] Procurement recommendation REJECTED. (Reason: {reason})")
            return "REJECTED", reason
        elif choice in ['Q', 'QUIT']:
            print("\n[STATUS] Decision deferred. Marked as PENDING.")
            return "PENDING", ""
        else:
            print("Invalid response. Please enter 'Y' for Yes, 'N' for No, or 'Q' to Quit.")

def display_previous_recommendations(history): # displays log of previous decisions  
    if not history:
        print("\nNo previous procurement recommendations found.")
        return
    
    print("\n--- PREVIOUS RECOMMENDATIONS & DECISIONS ---")
    for idx, record in enumerate(history, start=1):
        item_id = record.get('item_id', 'Unknown')
        action = record.get('action', 'N/A')
        status = record.get('approval_status', 'N/A')
        print(f"[{idx}] Item ID: {item_id} | Action: {action} | Status: {status}")
