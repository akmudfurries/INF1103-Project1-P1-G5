import ui_manager
import data_manager
import file_manager
import ai_manager

INVENTORY_FILE = "data/inventory.json"

def add_inventory_record():
    inventory_input = ui_manager.prompt_inventory_record()

    try:
        inventory_record = data_manager.build_inventory_record(
            # UI currently uses "item" as the item name.
            # data_manager requires "item_id", so the item name is temporarily used as the ID.
            # TODO: Replace with a dedicated item_id once the final data schema is agreed.
            item_id=inventory_input["item"],

            # Map UI field names to the field names expected by data_manager.
            item_name=inventory_input["item"],
            current_stock=inventory_input["current_stock"],
            # data_manager requires "weekly_usage", so the following is temporarily used as the ID.
            weekly_usage=inventory_input["avg_weekly_usage"],
            # data_manager requires "lead_time_weeks", so the following is temporarily used as the ID.
            
            lead_time_weeks=inventory_input["supplier_lead_time"],
            operational_notes=inventory_input["operational_notes"]
        )
    except ValueError as error:
        print(f"\n[ERROR] {error}")
        return

    records = file_manager.load_records(INVENTORY_FILE)

    success, error = data_manager.add_record(
        records,
        inventory_record,
        "item_id"
    )

    if not success:
        print(f"\n[ERROR] {error}")
        return

    if file_manager.save_records(INVENTORY_FILE, records):
        print("\n[STATUS] Inventory record saved successfully.")
    else:
        print("\n[ERROR] Failed to save inventory record.")

def view_inventory_records():
    records = file_manager.load_records(INVENTORY_FILE)

    ui_manager.display_inventory_records(records)        

def run_inventory_analysis():
    records = file_manager.load_records(INVENTORY_FILE)

    if not records:
        print("\nNo inventory records found.")
        return

    ui_manager.display_inventory_records(records)

    choice = input("\nEnter the inventory record number to analyse: ").strip()

    if not choice.isdigit():
        print("\n[ERROR] Please enter a valid record number.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(records):
        print("\n[ERROR] Invalid inventory record number.")
        return

    inventory = records[index]

    ai_assessment, error = ai_manager.get_ai_analysis(inventory)

    if error:
        print(f"\n[ERROR] {error}")
        return

    print("\n[AI ANALYSIS]")
    print(f"Demand Level: {ai_assessment['demand_level']}")
    print(f"Demand Trend: {ai_assessment['demand_trend']}")
    print(f"Supplier Issue: {ai_assessment['supplier_issue']}")
    print(f"Operational Importance: {ai_assessment['operational_importance']}")
    print(f"Reason: {ai_assessment['reason']}")



def main():
    ui_manager.print_header()

    while True:
        choice = ui_manager.get_main_menu_choice()

        if choice == "1":
            add_inventory_record()
            
        elif choice == "2":
            view_inventory_records()

        elif choice == "3":
            run_inventory_analysis()

        elif choice == "4":
            print("View previous procurement recommendations.")

        elif choice == "5":
            print("Exiting application.")
            break

        else:
            print("Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main()
