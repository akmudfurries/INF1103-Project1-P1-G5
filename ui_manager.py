import config


def print_header(): # display top app title banner
    print(config.BANNER_CHAR * config.LINE_WIDTH)
    print(f"{config.APP_TITLE.center(config.LINE_WIDTH)}")
    print(f"{config.APP_SUBTITLE.center(config.LINE_WIDTH)}")
    print(config.BANNER_CHAR * config.LINE_WIDTH)



def get_main_menu_choice(): # renders main CLI menu and captures user choice
    print("\n [ MAIN MENU ]")
    print("1. Add new inventory record")
    print("2. View stored inventory records")
    print("3. Run inventory analysis")
    print("4. View previous procurement recommendations")
    print("5. Exit")

    return input("\nSelect an option (1-5): ").strip()

def prompt_inventory_record(): # collects raw inventory item input fields
    print("\n" +config.DIVIDER_CHAR * config.LINE_WIDTH)
    print(" CREATE NEW INVENTORY RECORD ")
    print(config.DIVIDER_CHAR * config.LINE_WIDTH)

    item_id = input("Item ID / SKU: ").strip()
    item_name = input("Item Name: ").strip()
    category = input("Category: ").strip()
    stock_raw = input("Current Stock (units): ").strip()
    usage_raw = input("Average Weekly Usage (units): ").strip()
    lead_raw = input("Supplier Lead Time (weeks): ").strip()
    moq_raw = input("Minimum Order Quantity (units): ").strip()
    cost_raw = input("Unit Cost ($): ").strip()
    budget_raw = input("Available Budget ($): ").strip()
    notes = input("Operational Notes: ").strip()

# direct type conversion
    return { 
        "item_id": item_id if item_id else "ITEM_001",
        "item_name": item_name if item_name else "Unnamed Item",
        "category": category if category else "General",
        "current_stock": int(stock_raw) if stock_raw.isdigit() else 0,
        "weekly_usage": float(usage_raw) if usage_raw.replace('.', '', 1).isdigit() else 0.0,
        "lead_time_weeks": int(lead_raw) if lead_raw.isdigit() else 0,
        "minimum_order_quantity": int(moq_raw) if moq_raw.isdigit() else 0,
        "unit_cost": float(cost_raw) if cost_raw.replace('.', '', 1).isdigit() else 0.0,
        "available_budget": float(budget_raw) if budget_raw.replace('.', '', 1).isdigit() else 0.0,
        "operational_notes": notes if notes else "N/A"
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
    print(f"Current Stock:      {inventory['current_stock']} units")
    print(f"Weekly Usage:       {inventory['avg_weekly_usage']} units")
    print(f"Supplier Lead Time: {inventory['supplier_lead_time']} weeks")

    coverage = analysis_result.get('stock_coverage_weeks')
    coverage_str = f"{coverage:.1f} weeks" if coverage is not None else "N/A"
    print(f"Stock Coverage:     {coverage_str}")

    # ai assessment (ref to ai_manager.py)
    print("\n[AI Assessment]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Demand Level:           {ai_assessment.get('demand_level', 'N/A').upper()}")
    print(f"Demand Trend:           {ai_assessment.get('demand_trend', 'N/A').upper()}")
    print(f"Supplier Issue:         {ai_assessment.get('supplier_issue', 'N/A').upper()}")
    print(f"Operational Importance: {ai_assessment.get('operational_importance', 'N/A').upper()}")
    print(f"Reason:                 {ai_assessment.get('reason', 'N/A')}")

    # procurement analysis calculations (ref to business_rules.py)
    print("\n[Procurement Analysis]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Reorder Point:      {analysis_result.get('reorder_point', 0)} units")
    print(f"Recommended Order:  {analysis_result.get('recommended_order_quantity', 0)} units")
    print(f"Estimated Cost:     ${analysis_result.get('estimated_cost', 0.0):.2f}")
    print(f"Available Budget:   ${analysis_result.get('available_budget', 0.0):.2f}")

    # decision output and priority
    print("\n[Final Decision]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Priority:           {analysis_result.get('priority', 'NORMAL')}")
    print(f"Action:             {analysis_result.get('action', 'NO ACTION')}")

    escalation = "REQUIRED" if analysis_result.get('budget_escalation_required') else "NOT REQUIRED"
    print(f"Budget Escalation:  {escalation}")
    print(config.BANNER_CHAR * config.LINE_WIDTH)

def prompt_user_approval(): # prompts user to approve or reject the generated procurement decision
    while True:
        choice = input("\nDo you APPROVE this recommendation? (Y/N): ").strip().upper()
        if choice in ['Y', 'YES']:
            print("\n[STATUS] Procurement recommendation APPROVED and queued for persistence.")
            return "APPROVED"
        elif choice in ['N', 'NO']:
            reason = input("Enter reason for rejection/overriding decision: ").strip()
            print(f"\n[STATUS] Procurement recommendation REJECTED. (Reason: {reason})")
            return f"REJECTED: {reason}"
        else:
            print("Invalid response. Please enter 'Y' for Yes or 'N' for No.")

def display_previous_recommendations(history): # displays log of previous decisions
    print("\n" + config.BANNER_CHAR * config.LINE_WIDTH)
    print(" PREVIOUS RECOMMENDATIONS & DECISIONS ")
    print(config.DIVIDER_CHAR * config.LINE_WIDTH)
    
    if not history:
        print("No previous recommendations recorded.")
        return

    for idx, rec in enumerate(history, start=1):
        item_id = rec.get('item_id', 'Unknown')
        priority = rec.get('priority', 'N/A')
        action = rec.get('action', 'N/A')
        print(f"[{idx}] Item ID: {item_id} | Priority: {priority} | Action: {action}")
