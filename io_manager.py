import config
import validation
import textwrap


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
    return input("\nSelect an option (1-5): ").strip().lower()

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

    fields_to_prompt = [
        ("item_id", "Item Name / ID: "),
        ("category", "Category: "),
        ("Current Stock", "Current Stock (units): "),
        ("Average Weekly Usage", "Average Weekly Usage (units): "),
        ("Supplier Lead Time", "Supplier Lead Time (weeks): "),
        ("Minimum Order Quantity", "Minimum Order Quantity (units): "),
        ("Unit Cost", "Unit Cost ($): "),
        ("Available Budget", "Available Budget ($): "),
        ("operational_notes", "Operational Notes: ")
    ]

    collected = {}
    for key, prompt_text in fields_to_prompt:
        while True:
            val = _get_input_or_cancel(prompt_text)
            if val is None:
                return None
            
            is_valid, err_msg = validation.validate_single_field(key, val)
            if is_valid:
                if key in ["Current Stock", "Supplier Lead Time", "Minimum Order Quantity"]:
                    collected[key] = int(val)
                elif key in ["Average Weekly Usage", "Unit Cost", "Available Budget"]:
                    collected[key] = float(val)
                else:
                    collected[key] = val
                break
            else:
                print(f"  [!] Validation Error: {err_msg} Please try again.")

# mapped keys matching team schema
    return {
        "item_id": collected["item_id"],
        "item_name": collected["item_id"],
        "category": collected["category"],
        "current_stock": collected["Current Stock"],
        "weekly_usage": collected["Average Weekly Usage"],
        "lead_time_weeks": collected["Supplier Lead Time"],
        "moq": collected["Minimum Order Quantity"],
        "unit_cost": collected["Unit Cost"],
        "budget": collected["Available Budget"],
        "operational_notes": collected["operational_notes"]
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
        notes = item.get("operational_notes") or "None provided"

        print(f"\n[{idx}] {name} | Category: {cat} | Stock: {stock} units")
        print("    Operational Notes:")
        wrapped_notes = textwrap.fill(
            notes,
            width=75,
            initial_indent="    ",
            subsequent_indent="    "
        )
        print(wrapped_notes)

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
    wrapped_notes = textwrap.fill(
        inventory.get('operational_notes', 'None provided'),
        width=75,
        initial_indent="",
        subsequent_indent=""
    )
    print(f"Operational Notes: \n{wrapped_notes}\n")

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

    if "safety_stock" in analysis_result:
        print(f"Safety Stock:       {analysis_result['safety_stock']} units")

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
            while True:
                reason = input("Enter reason for rejection/overriding decision: ").strip()
                if reason:
                    break
                print("Reason cannot be empty. Please type a reason.")
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

    print("-" * config.LINE_WIDTH)
    choice = input("\nEnter record number to view full details (or 'q' to return):").strip()

    if choice.lower() in ['q', 'quit']:
        return

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(history):
            selected = history[idx]
            print("\n" + config.BANNER_CHAR * config.LINE_WIDTH)
            print(f" FULL DETAILS FOR RECORD #{idx + 1}".center(config.LINE_WIDTH))
            print(config.BANNER_CHAR * config.LINE_WIDTH)
            
            for key, value in selected.items():
                print(f"  {key.replace('_', ' ').title():<24}: {value}")
                
            print(config.BANNER_CHAR * config.LINE_WIDTH)
        else:
            print("\n[ERROR] Invalid record number.")
    else:
        print("\n[ERROR] Please enter a valid number.")
