
import pytest
from unittest.mock import Mock, call

from application_controller import ApplicationController
from models import ProcurementDecision


@pytest.fixture
def controller():
    io = Mock()
    ai = Mock()
    logic = Mock()
    data = Mock()

    return ApplicationController(io, ai, logic, data), io, ai, logic, data


@pytest.fixture
def inventory():
    record = Mock()
    record.item_id = "INV001"
    record.to_dict.return_value = {"item_id": "INV001"}
    return record


@pytest.fixture
def assessment():
    result = Mock()
    result.to_dict.return_value = {"demand_level": "HIGH"}
    return result


@pytest.fixture
def analysis_result():
    return {
        "recommended_quantity": 20,
        "priority": "HIGH",
        "action": "URGENT REORDER"
    }


def test_add_inventory_record_success(controller):
    ctrl, io, ai, logic, data = controller
    record = Mock()

    io.prompt_inventory_record.return_value = record
    data.add_inventory_record.return_value = (True, None)

    ctrl.add_inventory_record()

    data.add_inventory_record.assert_called_once_with(record)
    io.display_status_message.assert_called_once()


def test_add_inventory_record_cancelled(controller):
    ctrl, io, ai, logic, data = controller

    io.prompt_inventory_record.return_value = None

    ctrl.add_inventory_record()

    data.add_inventory_record.assert_not_called()


def test_view_inventory_records(controller, inventory):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = [inventory]

    ctrl.view_inventory_records()

    io.display_inventory_records.assert_called_once_with([inventory])


def test_remove_inventory_record_success(controller, inventory):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = [inventory]
    io.prompt_inventory_removal.return_value = "INV001"
    data.remove_inventory_record.return_value = (True, None)

    ctrl.remove_inventory_record()

    data.remove_inventory_record.assert_called_once_with("INV001")
    io.display_status_message.assert_called_once()


def test_remove_inventory_record_no_records(controller):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = []

    ctrl.remove_inventory_record()

    io.prompt_inventory_removal.assert_not_called()
    data.remove_inventory_record.assert_not_called()


def test_analysis_ai_failure(controller, inventory):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = [inventory]
    io.prompt_inventory_selection.return_value = "INV001"
    data.get_inventory_record.return_value = inventory
    ai.assess.return_value = (None, "AI service unavailable")

    ctrl.run_inventory_analysis()

    io.display_error.assert_called_with("AI service unavailable")
    data.create_procurement_record.assert_not_called()


def test_analysis_success_creates_pending_procurement(
    controller, inventory, assessment, analysis_result
):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = [inventory]
    io.prompt_inventory_selection.return_value = "INV001"
    data.get_inventory_record.return_value = inventory
    ai.assess.return_value = (assessment, None)
    logic.analyse_inventory.return_value = analysis_result
    data.create_procurement_record.return_value = (True, None)
    io.prompt_user_approval.return_value = ("DEFER", None)
    data.update_procurement_status.return_value = (True, None)

    ctrl.run_inventory_analysis()

    data.create_procurement_record.assert_called_once()

    decision = data.create_procurement_record.call_args.args[0]

    assert isinstance(decision, ProcurementDecision)
    assert decision.approval_status == "PENDING"
    assert decision.procurement_id is None

    data.update_procurement_status.assert_called_once_with(
        decision.procurement_id, "DEFER", None
    )


@pytest.mark.parametrize(
    "status, reason",
    [
        ("APPROVED", None),
        ("REJECTED", "Insufficient budget"),
        ("DEFER", None),
    ]
)
def test_update_procurement_status(controller, status, reason):
    ctrl, io, ai, logic, data = controller

    data.update_procurement_status.return_value = (True, None)

    ctrl.update_procurement_status("PROC001", status, reason)

    data.update_procurement_status.assert_called_once_with(
        "PROC001", status, reason
    )
    io.display_status_message.assert_called_once()


def test_update_procurement_status_failure(controller):
    ctrl, io, ai, logic, data = controller

    data.update_procurement_status.return_value = (
        False, "Procurement not found"
    )

    ctrl.update_procurement_status("PROC001", "APPROVED")

    io.display_error.assert_called_with("Procurement not found")


def test_view_previous_recommendations_empty(controller):
    ctrl, io, ai, logic, data = controller

    data.get_procurement_records.return_value = []

    ctrl.view_previous_recommendations()

    io.display_status_message.assert_called_once()
    io.display_previous_recommendations.assert_not_called()


def test_view_procurement_history(controller):
    ctrl, io, ai, logic, data = controller

    record = Mock()
    data.get_procurement_record.return_value = record
    data.get_procurement_history.return_value = [{"event_type": "CREATED"}]

    io.prompt_procurement_selection.return_value = "PROC001"
    io.prompt_record_action.return_value = ("VIEW", None)

    ctrl.view_historical_procurement_record([record])

    data.get_procurement_history.assert_called_once_with("PROC001")
    io.display_procurement_history.assert_called_once()


def test_delete_procurement_record(controller):
    ctrl, io, ai, logic, data = controller

    record = Mock()
    data.get_procurement_record.return_value = record
    data.delete_procurement_record.return_value = (True, None)

    io.prompt_procurement_selection.return_value = "PROC001"
    io.prompt_record_action.return_value = ("DELETE", None)

    ctrl.view_historical_procurement_record([record])

    data.delete_procurement_record.assert_called_once_with("PROC001")
    io.display_status_message.assert_called_once()


def test_simulation_cancelled(controller, inventory, assessment, analysis_result):
    ctrl, io, ai, logic, data = controller

    data.get_inventory_records.return_value = [inventory]
    io.prompt_inventory_selection.return_value = "INV001"
    data.get_inventory_record.return_value = inventory
    ai.assess.return_value = (assessment, None)
    logic.analyse_inventory.return_value = analysis_result
    io.prompt_simulation_parameters.return_value = None

    ctrl.run_procurement_simulation()

    logic.simulate_procurement.assert_not_called()
    io.display_simulation_comparison.assert_not_called()


def test_simulation_success(controller, inventory, assessment, analysis_result):
    ctrl, io, ai, logic, data = controller

    simulated_result = {"recommended_quantity": 30}

    data.get_inventory_records.return_value = [inventory]
    io.prompt_inventory_selection.return_value = "INV001"
    data.get_inventory_record.return_value = inventory
    ai.assess.return_value = (assessment, None)
    logic.analyse_inventory.return_value = analysis_result
    io.prompt_simulation_parameters.return_value = (10, 4)
    logic.simulate_procurement.return_value = simulated_result

    ctrl.run_procurement_simulation()

    ai.assess.assert_called_once_with(inventory)
    logic.simulate_procurement.assert_called_once_with(
        inventory, assessment, 10, 4
    )
    io.display_simulation_comparison.assert_called_once_with(
        analysis_result, simulated_result
    )

    data.create_procurement_record.assert_not_called()
