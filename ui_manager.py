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
    
    item = input("Item Name: ").strip()
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
        "item": item if item else "Unnamed Item",
        "category": category if category else "General",
        "current_stock": int(stock_raw) if stock_raw.isdigit() else 0,
        "avg_weekly_usage": int(usage_raw) if usage_raw.isdigit() else 0,
        "supplier_lead_time": int(lead_raw) if lead_raw.isdigit() else 0,
        "min_order_qty": int(moq_raw) if moq_raw.isdigit() else 0,
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
        print(f"[{idx}] {item['item']} | Category: {item['category']} | Stock: {item['current_stock']} units")

def display_full_procurement_report(inventory, ai_assessment, analysis_result): # renders complete analysis output and metrics
    print("\n" + config.BANNER_CHAR * config.LINE_WIDTH)
    print(f"{config.APP_TITLE:^{config.LINE_WIDTH}}")
    print(config.BANNER_CHAR * config.LINE_WIDTH)
    print(f"Item Name: {inventory['item']} ({inventory['category']})")

    # quantitative inventory data
    print("\n[Inventory Data]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Current Stock:      {inventory['current_stock']} units")
    print(f"Weekly Usage:       {inventory['avg_weekly_usage']} units")
    print(f"Supplier Lead Time: {inventory['supplier_lead_time']} weeks")
    print(f"Stock Coverage:     {analysis_result.get('stock_coverage', 0.0):.1f} weeks")

    # ai assessment
    print("\n[AI Assessment]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Demand Level:       {ai_assessment.get('demand_level', 'N/A').upper()}")
    print(f"Demand Trend:       {ai_assessment.get('demand_trend', 'N/A').upper()}")
    print(f"Stock Condition:    {ai_assessment.get('stock_condition', 'N/A').upper()}")
    print(f"Stockout Risk:      {ai_assessment.get('stockout_risk', 'N/A').upper()}")

    # procurement analysis calculations
    print("\n[Procurement Analysis]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Reorder Point:      {analysis_result.get('reorder_point', 0)} units")
    print(f"Recommended Order:  {analysis_result.get('recommended_order', 0)} units")
    print(f"Estimated Cost:     ${analysis_result.get('estimated_cost', 0.0):.2f}")
    print(f"Available Budget:   ${inventory['available_budget']:.2f}")

    # decision output and priority
    print("\n[Final Decision]")
    print(config.DIVIDER_CHAR * 30)
    print(f"Priority:           {analysis_result.get('priority', 'NORMAL')}")
    print(f"Action:             {analysis_result.get('action', 'NO ACTION')}")
    print(f"Budget Escalation:  {analysis_result.get('budget_escalation', 'NOT REQUIRED')}")
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
        print(f"[{idx}] Item: {rec['item']} | Priority: {rec['priority']} | Decision Status: {rec['approval_status']}")
