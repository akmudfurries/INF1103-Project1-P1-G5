from models import ProcurementDecision

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
        inventory_record = self.io_manager.prompt_inventory_record()

        if inventory_record is None:
            return

        try:
            success, error = self.data_manager.add_inventory_record(
                inventory_record
            )

            if success:
                self.io_manager.display_status_message(
                    "Inventory record added successfully."
                )
            else:
                self.io_manager.display_error(error)

        except Exception as error:
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
        try:
            records = self.data_manager.get_inventory_records()

            if not records:
                self.io_manager.display_status_message(
                    "No inventory records available for analysis."
                )
                return

            item_id = self.io_manager.prompt_inventory_selection(records)

            if item_id is None:
                return

            inventory = self.data_manager.get_inventory_record(item_id)

            if inventory is None:
                self.io_manager.display_error(
                    "Inventory record could not be found."
                )
                return

            assessment, error = self.ai_manager.assess(inventory)

            if assessment is None:
                self.io_manager.display_error(error)
                return

            result = self.logic_manager.analyse_inventory(
                inventory, assessment
            )

            self.io_manager.display_full_procurement_report(
                inventory, assessment, result
            )

            decision = ProcurementDecision(
                procurement_id=None,
                item_id=inventory.item_id,
                recommended_quantity=result["recommended_quantity"],
                priority=result["priority"],
                action=result["action"],
                approval_status="PENDING",
                rejection_reason=None,
                timestamp=None,
                status_updated=None,
                inventory_snapshot=inventory.to_dict(),
                ai_assessment=assessment.to_dict(),
                analysis_result=result
            )

            success, error = self.data_manager.create_procurement_record(
                decision
            )

            if not success:
                self.io_manager.display_error(error)
                return

            self.io_manager.display_status_message(
                "Procurement recommendation saved."
            )

            status, rejection_reason = (
                self.io_manager.prompt_user_approval()
            )

            self.update_procurement_status(
                decision.procurement_id,
                status,
                rejection_reason
            )

        except Exception as error:
            self.io_manager.display_error(str(error))

    def view_previous_recommendations(self):
        try:
            records = self.data_manager.get_procurement_records()

            if not records:
                self.io_manager.display_status_message(
                    "No previous procurement recommendations available."
                )
                return

            self.io_manager.display_previous_recommendations(records)

            self.view_historical_procurement_record()

        except Exception as error:
            self.io_manager.display_error(str(error))

    def view_historical_procurement_record(self):
        try:
            records = self.data_manager.get_procurement_records()

            if not records:
                self.io_manager.display_status_message(
                    "No procurement records available."
                )
                return

            procurement_id = (
                self.io_manager.prompt_procurement_selection(records)
            )

            if procurement_id is None:
                return

            record = self.data_manager.get_procurement_record(
                procurement_id
            )

            if record is None:
                self.io_manager.display_error(
                    "Procurement record could not be found."
                )
                return

            action, rejection_reason = (
                self.io_manager.prompt_record_action(record)
            )

            if action == "VIEW":
                self.io_manager.display_historical_procurement_report(
                    record
                )

                history = self.data_manager.get_procurement_history(
                    procurement_id
                )

                self.io_manager.display_procurement_history(history)

            elif action == "APPROVE":
                self.update_procurement_status(
                    procurement_id, "APPROVED"
                )

            elif action == "REJECT":
                self.update_procurement_status(
                    procurement_id,
                    "REJECTED",
                    rejection_reason
                )

            elif action == "DELETE":
                success, error = (
                    self.data_manager.delete_procurement_record(
                        procurement_id
                    )
                )

                if success:
                    self.io_manager.display_status_message(
                        "Procurement record deleted successfully."
                    )
                else:
                    self.io_manager.display_error(error)

            elif action == "BACK":
                return

            else:
                self.io_manager.display_error(
                    "Invalid procurement record action."
                )

        except Exception as error:
            self.io_manager.display_error(str(error))

    def update_procurement_status(self, procurement_id, status, rejection_reason=None):
        try:
            success, error = self.data_manager.update_procurement_status(
                procurement_id,
                status,
                rejection_reason
            )

            if success:
                if status == "DEFER":
                    self.io_manager.display_status_message(
                        "Procurement decision deferred. It remains pending."
                    )
                else:
                    self.io_manager.display_status_message(
                        f"Procurement decision updated to {status}."
                    )
            else:
                self.io_manager.display_error(error)

        except Exception as error:
            self.io_manager.display_error(str(error))

    def run_procurement_simulation(self):
        try:
            records = self.data_manager.get_inventory_records()

            if not records:
                self.io_manager.display_status_message(
                    "No inventory records available for simulation."
                )
                return

            item_id = self.io_manager.prompt_inventory_selection(records)

            if item_id is None:
                return

            inventory = self.data_manager.get_inventory_record(item_id)

            if inventory is None:
                self.io_manager.display_error(
                    "Inventory record could not be found."
                )
                return

            assessment, error = self.ai_manager.assess(inventory)

            if assessment is None:
                self.io_manager.display_error(error)
                return

            current_result = self.logic_manager.analyse_inventory(
                inventory, assessment
            )

            parameters = self.io_manager.prompt_simulation_parameters()

            if parameters is None:
                return

            simulated_usage, simulated_lead_time = parameters

            simulated_result = self.logic_manager.simulate_procurement(
                inventory,
                assessment,
                simulated_usage,
                simulated_lead_time
            )

            self.io_manager.display_simulation_comparison(
                current_result,
                simulated_result
            )

        except Exception as error:
            self.io_manager.display_error(str(error))