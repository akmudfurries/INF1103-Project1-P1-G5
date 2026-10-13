import logic_manager
import io_manager
import data_manager
import file_manager
import ai_manager
import config

INVENTORY_FILE = "data/inventory.json"
DECISIONS_FILE = "data/procurement_decisions.json"

def add_inventory_record():
    inventory_input = io_manager.prompt_inventory_record()
    if not inventory_input:
        return

    try:
        inventory_record = data_manager.build_inventory_record(
            # io_manager now returns exact keys required by data_manager.build_inventory_record, so no need for mapping.
            item_id=inventory_input["item_id"],
            item_name=inventory_input["item_name"],
            current_stock=inventory_input["current_stock"],
            weekly_usage=inventory_input["weekly_usage"],
            lead_time_weeks=inventory_input["lead_time_weeks"],
            operational_notes=inventory_input["operational_notes"]
        )

        # optional fields returned by io_manager
        inventory_record["category"] = inventory_input["category"]
        inventory_record["moq"] = inventory_input["moq"]
        inventory_record["unit_cost"] = inventory_input["unit_cost"]
        inventory_record["budget"] = inventory_input["budget"]

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


# fixed ui schema mismatch n removed temporary adapter function

def view_inventory_records():
    records = file_manager.load_records(INVENTORY_FILE)
    io_manager.display_inventory_records(records)
      

def run_inventory_analysis():
    records = file_manager.load_records(INVENTORY_FILE)

    if not records:
        print("\nNo inventory records found.")
        return
    
# removed temporary ui schema adaptor function

    io_manager.display_inventory_records(records)

    choice = input("\nEnter the inventory record number to analyse (or 'q' to cancel): ").strip()
    if choice.lower() in ['q', 'quit']:
        return

    if not choice.isdigit():
        print("\n[ERROR] Please enter a valid record number.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(records):
        print("\n[ERROR] Invalid inventory record number.")
        return

    inventory = records[index]

    # AI integration is implemented but requires GEMINI_API_KEY to run.
    # TODO: Test with a valid API key before final integration testing.
    ai_assessment, error = ai_manager.get_ai_analysis(inventory) # run ai analysis

    if error:
        print(f"\n[ERROR] {error}")
        return

    # run quantitative business rules analysis
    try:
        analysis_result = logic_manager.analyse_inventory(inventory, ai_assessment)
    except ValueError as err:
        print(f"\n[ERROR] Business Rule Calculation Error: {err}")
        return

    # display full report to user (ui)
    io_manager.display_full_procurement_report(inventory, ai_assessment, analysis_result)

    # Prompt user for approval decision and rejection reason
    approval_status, rejection_reason = io_manager.prompt_user_approval()

    # Create procurement decision record
    try:
        procurement_record = data_manager.create_procurement_from_business_rule(
            inventory["item_id"],
            analysis_result,
            approval_status,
            rejection_reason if approval_status == "REJECTED" else None
        )
    except (ValueError, KeyError) as error:
        print(f"\n[ERROR] Failed to create procurement record: {error}")
        return

    decisions = file_manager.load_records(DECISIONS_FILE)
    # Procurement history can contain multiple decisions for one inventory item.
    decisions.append(procurement_record)

    if file_manager.save_records(DECISIONS_FILE, decisions):
        print("[STATUS] Procurement decision saved successfully.")
    else:
        print("[ERROR] Failed to save procurement decision.")


def view_previous_recommendations():
    decisions = file_manager.load_records(DECISIONS_FILE)
    io_manager.display_previous_recommendations(decisions)


def main():
    io_manager.print_header()

    while True:
        choice = io_manager.get_main_menu_choice()

        if choice == "1":
            add_inventory_record()
            
        elif choice == "2":
            view_inventory_records()

        elif choice == "3":
            run_inventory_analysis()

        elif choice == "4":
            view_previous_recommendations()

        elif choice in ["5", "q", "quit"]:
            print("Exiting application.")
            break

        else:
            print("Please enter 1, 2, 3, 4 or '5' to exit application.")

if __name__ == "__main__":
    main()
