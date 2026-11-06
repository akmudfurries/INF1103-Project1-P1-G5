from models import InventoryRecord

class ApplicationController:

    def __init__(self, io_manager, ai_manager, logic_manager, data_manager):
        self.io_manager = io_manager
        self.ai_manager = ai_manager
        self.logic_manager = logic_manager
        self.data_manager = data_manager

    def run(self):
        self.io_manager.print_header()

        while True:
            choice = self.io_manager.get_main_menu_choice()

            if choice == "1":
                self.add_inventory_record()

            elif choice == "2":
                self.view_inventory_records()

            elif choice == "3":
                self.run_inventory_analysis()

            elif choice == "4":
                self.view_previous_recommendations()

            elif choice == "5":
                self.remove_inventory_record()

            elif choice == "6":
                self.run_procurement_simulation()

            elif choice in ["7", "q", "quit"]:
                self.io_manager.display_status_message("Exiting application.")
                break

            else:
                self.io_manager.display_error(
                    "Invalid choice. Please select an available menu option."
                )

    def add_inventory_record(self):
        inventory_data = self.io_manager.prompt_inventory_record()

        if inventory_data is None:
            return

        try:
            inventory_record = InventoryRecord.from_dict(inventory_data)

            success, error = self.data_manager.add_inventory_record(
                inventory_record
            )

            if success:
                self.io_manager.display_status_message(
                    "Inventory record added successfully."
                )
            else:
                self.io_manager.display_error(error)

        except (ValueError, TypeError, KeyError) as error:
            self.io_manager.display_error(str(error))

    def view_inventory_records(self):
        try:
            records = self.data_manager.get_inventory_records()
            self.io_manager.display_inventory_records(records)

        except Exception as error:
            self.io_manager.display_error(str(error))

    def remove_inventory_record(self):
        try:
            records = self.data_manager.get_inventory_records()

            if not records:
                self.io_manager.display_status_message(
                    "No inventory records available."
                )
                return

            item_id = self.io_manager.prompt_inventory_removal(records)

            if item_id is None:
                return

            success, error = self.data_manager.remove_inventory_record(
                item_id
            )

            if success:
                self.io_manager.display_status_message(
                    "Inventory record removed successfully."
                )
            else:
                self.io_manager.display_error(error)

        except Exception as error:
            self.io_manager.display_error(str(error))

    def run_inventory_analysis(self):
        pass

    def view_previous_recommendations(self):
        pass

    def view_historical_procurement_record(self):
        pass

    def update_procurement_status(self, procurement_id, status, rejection_reason=None):
        pass

    def run_procurement_simulation(self):
        pass