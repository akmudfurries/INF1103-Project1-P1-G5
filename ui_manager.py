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
        