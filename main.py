import ui_manager
import data_manager
import file_manager

INVENTORY_FILE = "data/inventory.json"

def add_inventory_record():
    inventory_input = ui_manager.prompt_inventory_record()

    try:
        inventory_record = data_manager.build_inventory_record(
            item_id=inventory_input["item_id"],
            item_name=inventory_input["item_name"],
            current_stock=inventory_input["current_stock"],
            weekly_usage=inventory_input["weekly_usage"],
            lead_time_weeks=inventory_input["lead_time_weeks"],
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

def main():
    ui_manager.print_header()

    while True:
        choice = ui_manager.get_main_menu_choice()

        if choice == "1":
            print("Add inventory.")
            add_inventory_record()
            
        elif choice == "2":
            print("View inventory.")
            view_inventory_records()

        elif choice == "3":
            print("AI analysis.")

        elif choice == "4":
            print("View previous procurement recommendations.")

        elif choice == "5":
            print("Exiting application.")
            break

        else:
            print("Please enter 1, 2, 3, 4 or 5.")

if __name__ == "__main__":
    main()
