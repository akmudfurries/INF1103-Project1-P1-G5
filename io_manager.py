import config
import validation
import textwrap
from datetime import datetime

class IOManager:
    def __init__(self):
        pass

    def format_timestamp(self, value):
    # Turns '2026-10-14T16:54:03' into '14 Oct 2026, 04:54 PM'
        try:
            return datetime.fromisoformat(value).strftime("%d %b %Y, %I:%M %p")
        except (TypeError, ValueError):
            return value or "N/A"

    def print_section_heading(self, title, width=50):
        print("\n" + "=" * width)
        print(title.center(width))
        print("=" * width)

    def print_header(self): # display top app title banner
        print(config.BANNER_CHAR * config.LINE_WIDTH)
        print(f"{config.APP_TITLE.center(config.LINE_WIDTH)}")
        print(f"{config.APP_SUBTITLE.center(config.LINE_WIDTH)}")
        print(config.BANNER_CHAR * config.LINE_WIDTH)

    def get_main_menu_choice(self): # renders main CLI menu with quit and captures user choice
        print("\n [ MAIN MENU ]")
        print("1. Add new inventory record")
        print("2. View stored inventory records")
        print("3. Run inventory analysis")
        print("4. View previous procurement recommendations")
        print("5. Remove inventory record")
        print("6. What-if Procurement Scenario Simulation")
        print("7. Exit")
        return input("\nSelect an option (1-7): ").strip().lower()

    def _get_input_or_cancel(self, prompt_text):
    # helper to catch 'q' or 'quit' at any prompt.
        val = input(prompt_text).strip()
        if val.lower() in ['q', 'quit']:
            print("\n[!] Operation cancelled by user.")
            return None
        return val

    def display_status_message(self, message, success=True):
        prefix = "[STATUS]" if success else "[ERROR]"
        print(f"\n{prefix} {message}")

    def display_error(self, message):
        print(f"\n[ERROR] {message}")

    def prompt_inventory_record(self): # collects raw inventory item input fields
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
                val = self._get_input_or_cancel(prompt_text)
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

    def display_inventory_records(self, records): # displays saved inventory records
        if not records:
             print("\nNo inventory records found.")
             return

        self.print_section_heading("STORED INVENTORY RECORDS")
        for idx, item in enumerate(records, start=1):
            # support both objects and dictionaries
            name = getattr(item, "item_name", None) or (item.get("item_name") if isinstance(item, dict) else None) or (item.get("item") if isinstance(item, dict) else "Unknown Item")
            cat = getattr(item, "category", None) or (item.get("category", "General") if isinstance(item, dict) else "General")
            stock = getattr(item, "current_stock", None) if not isinstance(item, dict) else item.get("current_stock", 0)
            notes = getattr(item, "operational_notes", None) or (item.get("operational_notes") if isinstance(item, dict) else "None provided")

            print(f"\n[{idx}] {name} | Category: {cat} | Stock: {stock} units")
            print("    Operational Notes:")
            wrapped_notes = textwrap.fill(
                str(notes),
                width=50,
                initial_indent="    ",
                subsequent_indent="    "
            )
            print(wrapped_notes)

    def prompt_inventory_selection(self, records): # prompts user to select an inventory record for analysis
        if not records:
            print("\nNo inventory records found.")
            return None

        self.display_inventory_records(records)
        choice = input("\nEnter the record number to select (or 'q' to cancel): ").strip()
        if choice.lower() in ["q", "quit"]:
            return None
        if not choice.isdigit() or not 1 <= int(choice) <= len(records):
            print("Invalid record number.")
            return None
        selected = records[int(choice) - 1]
        return getattr(selected, "item_id", None) or (selected.get("item_id")) 

    def prompt_inventory_removal(self, records): # prompts user to select an inventory record for removal
        if not records:
            print("\nNo inventory records found.")
            return None
        
        self.display_inventory_records(records)

        while True:
            choice = input("\nEnter the record number to remove (or 'q' to cancel): ").strip()
            if choice.lower() in ["q", "quit"]:
                print("\n[!] Removal cancelled by user.")
                return None
            if not choice.isdigit() or not 1 <= int(choice) <= len(records):
                print("Invalid record number. Please try again")
                continue

            index = int(choice) - 1
            selected = records[int(choice) - 1]

            # support both domain objects and dictionaries representations safely
            name = getattr(selected, "item_name", None) or (selected.get("item_name") if isinstance(selected, dict) else selected.get("item_id", "this item"))
            item_id = getattr(selected, "item_id", None) or (selected.get("item_id") if isinstance(selected, dict) else None)
            confirm = input(f"Permanently remove '{name}'? (Y/N): ").strip().upper()
            if confirm in ["Y", "YES"]:
                return item_id
            print("Removal cancelled. Returning to list...")
            return None

    def display_full_procurement_report(self, inventory, ai_assessment, analysis_result): # renders complete analysis output and metrics
        print("\n" + config.BANNER_CHAR * config.LINE_WIDTH)
        print(f"{config.APP_TITLE:^{config.LINE_WIDTH}}")
        print(config.BANNER_CHAR * config.LINE_WIDTH)

        item_name = getattr(inventory, 'item_name', None) or (inventory.get('item_name') if isinstance(inventory, dict) else None) or (inventory.get('item', 'N/A') if isinstance(inventory, dict) else 'N/A')
        category = getattr(inventory, 'category', None) or (inventory.get('category', 'General') if isinstance(inventory, dict) else 'General')
        print(f"Item Name: {item_name} ({category})")

    # quantitative inventory data
        self.print_section_heading("Inventory Data")
        stock_val = getattr(inventory, 'current_stock', 0) if not isinstance(inventory, dict) else inventory.get('current_stock', 0)
        usage_val = getattr(inventory, 'weekly_usage', 0.0) if not isinstance(inventory, dict) else inventory.get('weekly_usage', 0.0)
        lead_val = getattr(inventory, 'lead_time_weeks', 0) if not isinstance(inventory, dict) else inventory.get('lead_time_weeks', 0)
        notes_val = getattr(inventory, 'operational_notes', 'None provided') if not isinstance(inventory, dict) else inventory.get('operational_notes', 'None provided')
          
        print(f"Current Stock:      {stock_val} units")
        print(f"Weekly Usage:       {usage_val} units")
        print(f"Supplier Lead Time: {lead_val} weeks")
        wrapped_notes = textwrap.fill(
            str(notes_val),
            width=50,
            initial_indent="",
            subsequent_indent=""
        )
        print(f"Operational Notes: \n{wrapped_notes}\n")

        coverage = analysis_result.get('stock_coverage')
        coverage_str = f"{coverage:.1f} weeks" if coverage is not None else "N/A"
        print(f"Stock Coverage:     {coverage_str}")

        # ai assessment (ref to ai_manager.py  / business_rules.py)
        self.print_section_heading("AI Assessment")
        print(f"Demand Level:           {ai_assessment.get('demand_level', 'N/A').upper()}")
        print(f"Demand Trend:           {ai_assessment.get('demand_trend', 'N/A').upper()}")
        print(f"Supply Risk:            {ai_assessment.get('supply_risk', 'N/A').upper()}")
        print(f"Operational Importance: {ai_assessment.get('operational_importance', 'N/A').upper()}")
        wrapped_reason = textwrap.fill(
            ai_assessment.get('reason', 'N/A'),
            width=50,
            initial_indent="",
            subsequent_indent=""
        )
        print(f"Reason: \n{wrapped_reason}")
    
        # procurement analysis calculations (ref to business_rules.py)
        self.print_section_heading("Procurement Analysis")
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
        self.print_section_heading("Final Decision")
        print(f"Priority:           {analysis_result.get('priority', 'NORMAL')}")
        print(f"Action:             {analysis_result.get('action', 'NO ACTION')}")

        if "budget_escalation" in analysis_result:
            escalation = "REQUIRED" if analysis_result.get('budget_escalation') else "NOT REQUIRED"
            print(f"Budget Escalation:  {escalation}")
    

        print(config.BANNER_CHAR * config.LINE_WIDTH)

    def prompt_user_approval(self): # prompts user to approve or reject the generated procurement decision or quit
        while True:
            choice = input("\nDo you APPROVE this recommendation? (Y/N/Defer/Quit): ").strip().upper()
            if choice in ['Y', 'YES']:
                print("\n[STATUS] Procurement recommendation APPROVED.")
                return "APPROVED", None
            elif choice in ['N', 'NO']:
                while True:
                    reason = input("Enter reason for rejection/overriding decision: ").strip()
                    if reason:
                        print(f"\n[STATUS] Procurement recommendation REJECTED. (Reason: {reason})")
                        return "REJECTED", reason

                    print("[ERROR] A rejection reason is required.")

            elif choice in ['D','DEFER','Q', 'QUIT']:
                print("\n[STATUS] Decision deferred. Marked as PENDING.")
                return "DEFER", None
            else:
                print("Invalid response. Please enter 'Y' for Yes, 'N' for No, 'D' to Defer or 'Q' to Quit.")

    def display_previous_recommendations(self, records):
        self.print_section_heading("PREVIOUS PROCUREMENT ASSESSMENTS")
        if not records:
            print("No previous procurement assessments found.")
            return None

        for idx, record in enumerate(records, start=1):
            item_id = record.get("item_id", "Unknown")
            action = record.get("action", "N/A")
            status = record.get("approval_status", "N/A")
            timestamp = self.format_timestamp(record.get("timestamp"))
            print(f"[{idx}] Item ID: {item_id} | Action: {action} | Status: {status} | Date: {timestamp}")

        while True:
            choice = input("\nEnter assessment number to view details, or 'q' to return: ").strip()

            if choice.lower() in ["q", "quit"]:
                return None

            if not choice.isdigit():
                print("Invalid input. Enter a number or 'q' to quit.")
                continue
            record_number = int(choice)
            if record_number < 1 or record_number > len(records):
                print("Invalid assessment number.")
                continue
            return records[record_number - 1].get("procurement_id")
        
    def print_wrapped_field(self, label, value, width=50):
        text = str(value or "N/A")
        wrapped_text = textwrap.fill(text, width=width)
        print(f"{label}: \n{wrapped_text}")

    def display_historical_procurement_report(self, record):
        self.print_section_heading("HISTORICAL PROCUREMENT ASSESSMENT")
        print(f"Procurement ID: {record.get('procurement_id', 'N/A')}")
        print(f"Item ID: {record.get('item_id', 'N/A')}")
        print(f"Date: {self.format_timestamp(record.get('timestamp'))}")
        if record.get("status_updated"):
            print(f"Status Last Updated: {self.format_timestamp(record.get('status_updated'))}")
        print(f"Decision: {record.get('approval_status', 'N/A')}")
        print(f"Action: {record.get('action', 'N/A')}")
        print(f"Recommended Quantity: {record.get('recommended_quantity', 'N/A')}")
        print(f"Priority: {record.get('priority', 'N/A')}")

        inventory = record.get("inventory_snapshot") or {}
        ai_assessment = record.get("ai_assessment") or {}
        analysis = record.get("analysis_result") or {}

        self.print_section_heading("ORIGINAL INVENTORY DETAILS")
        if inventory:
            for field, value in inventory.items():
                label = field.replace("_", " ").title()

                if field == "operational_notes":
                    self.print_wrapped_field(label, value)
                else:
                    print(f"{label}: {value}")
        else:
            print("No historical inventory snapshot available.")

        self.print_section_heading("AI ASSESSMENT")
        if ai_assessment:
            for field, value in ai_assessment.items():
                label = field.replace("_", " ").title()

                if field == "reason":
                    self.print_wrapped_field(label, value)
                else:
                    print(f"{label}: {value}")
        else:
            print("No historical AI assessment available.")

        self.print_section_heading("PROCUREMENT ANALYSIS")
        if analysis:
            for field, value in analysis.items():
                print(f"{field.replace('_', ' ').title()}: {value}")
        else:
            print("No historical analysis result available.")

        rejection_reason = record.get("rejection_reason")
        if rejection_reason:
            print(f"\nRejection Reason: {rejection_reason}")

    def display_procurement_history(self, history):
        self.print_section_heading("PROCUREMENT STATUS HISTORY")
        if not history:
            print("No history events recorded.")
            return
        for h in history:
            t = self.format_timestamp(h.get("changed_at"))
            ev = h.get("event_type", "UPDATE")
            prev = h.get("previous_status", "None")
            new = h.get("new_status", "N/A")
            reason = h.get("reason")
            print(f"[{t}] Event: {ev} | Status: {prev} -> {new}" + (f" | Reason: {reason}" if reason else ""))

    def prompt_record_action(self, record):
        self.print_section_heading("Record Actions")
        print("1. Change approval status")
        print("2. Delete this record")
        print("3. Back to list\n")

        while True:
            choice = input("Select an option (1-3): ").strip()

            if choice == "1":
                current = record.get("approval_status")
                options = [s for s in ["PENDING", "APPROVED", "REJECTED"] if s != current]

                print(f"\nCurrent status: {current}")
                for number, status in enumerate(options, start=1):
                    print(f"{number}. {status}")

                picked = input(f"Choose new status (1-{len(options)}, or 'q' to cancel): ").strip()
                if picked.lower() in ["q", "quit"]:
                    return "BACK", None
                if not picked.isdigit() or not 1 <= int(picked) <= len(options):
                    print("Invalid choice.")
                    continue

                new_status = options[int(picked) - 1]
                reason = None

                if new_status == "REJECTED":
                    reason = ""
                    while not reason:
                        reason = input("Enter reason for rejection: ").strip()
                        if not reason:
                            print("[ERROR] A rejection reason is required.")

                # APPROVED / PENDING must clear any old rejection reason
                return "UPDATE", {"approval_status": new_status, "rejection_reason": reason}

            elif choice == "2":
                confirm = input("Delete this record permanently? (Y/N): ").strip().upper()
                if confirm in ["Y", "YES"]:
                    return "DELETE", None
                print("Delete cancelled.")
                return "BACK", None

            elif choice == "3":
                return "BACK", None

            else:
                print("Please enter 1, 2 or 3.")

def prompt_procurement_selection(self, records):
    return self.display_previous_recommendations(records)