import os
import sys
import unittest

# Let the tests import the project modules when run from any folder.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logic_manager
from logic_manager import LogicManager
from models import AIAssessment, InventoryRecord


def make_assessment(trend="stable", supply="medium", importance="medium"):
    # Fixed assessment: no live AI response is ever needed.
    return AIAssessment(
        demand_level="medium",
        demand_trend=trend,
        supply_risk=supply,
        operational_importance=importance,
        reason="Fixed assessment for testing.",
    )


def make_record(stock=18, usage=8, lead=3, moq=20, unit_cost=35, budget=2000):
    return InventoryRecord(
        item_id="INV007",
        item_name="Pressure Sensor",
        current_stock=stock,
        weekly_usage=usage,
        lead_time_weeks=lead,
        operational_notes="Delayed supplier",
        moq=moq,
        unit_cost=unit_cost,
        budget=budget,
    )


class LogicManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.logic = LogicManager()
        self.assessment = make_assessment()


class TestAnalysis(LogicManagerTestCase):
    def test_inv007_pressure_sensor_regression(self):
        result = self.logic.analyse_inventory(make_record(), self.assessment)
        self.assertEqual(result["safety_stock"], 8)
        self.assertEqual(result["reorder_point"], 32)
        self.assertEqual(result["recommended_quantity"], 30)
        self.assertEqual(result["priority"], "HIGH")
        self.assertEqual(result["action"], "URGENT REORDER")
        self.assertEqual(result["estimated_cost"], 1050)
        self.assertFalse(result["budget_escalation"])
        self.assertEqual(result["stock_coverage"], 2.25)
        self.assertEqual(result["stock_condition"], "at_risk")
        self.assertEqual(result["stockout_risk"], "high")

    def test_result_has_all_required_fields(self):
        result = self.logic.analyse_inventory(make_record(), self.assessment)
        for field in (
            "stock_coverage", "safety_stock", "reorder_point", "stock_condition",
            "stockout_risk", "recommended_quantity", "priority", "action",
            "estimated_cost", "budget_escalation",
        ):
            self.assertIn(field, result)

    def test_zero_weekly_usage(self):
        result = self.logic.analyse_inventory(make_record(stock=50, usage=0), self.assessment)
        self.assertIsNone(result["stock_coverage"])
        self.assertEqual(result["recommended_quantity"], 0)
        self.assertEqual(result["action"], "MONITOR")
        self.assertEqual(result["stock_condition"], "healthy")
        self.assertEqual(result["stockout_risk"], "low")

    def test_no_reorder_when_weekly_usage_is_zero(self):
        # Even with no stock at all, zero usage must not trigger a reorder.
        result = self.logic.analyse_inventory(make_record(stock=0, usage=0), self.assessment)
        self.assertEqual(result["recommended_quantity"], 0)
        self.assertEqual(result["action"], "MONITOR")
        self.assertEqual(result["estimated_cost"], 0)

    def test_zero_current_stock(self):
        result = self.logic.analyse_inventory(
            make_record(stock=0, usage=5, lead=2, moq=0), self.assessment
        )
        # safety 5, reorder point 15, target 25, shortage 25
        self.assertEqual(result["reorder_point"], 15)
        self.assertEqual(result["recommended_quantity"], 25)
        self.assertEqual(result["stock_coverage"], 0)
        self.assertEqual(result["stock_condition"], "critical")
        self.assertEqual(result["stockout_risk"], "high")
        self.assertEqual(result["priority"], "HIGH")
        self.assertEqual(result["action"], "URGENT REORDER")

    def test_moq_is_enforced_when_larger_than_shortage(self):
        # safety 5, reorder point 10, target 20, shortage 10
        result = self.logic.analyse_inventory(
            make_record(stock=10, usage=5, lead=1, moq=50), self.assessment
        )
        self.assertEqual(result["recommended_quantity"], 50)

    def test_shortage_is_used_when_larger_than_moq(self):
        result = self.logic.analyse_inventory(
            make_record(stock=10, usage=5, lead=1, moq=5), self.assessment
        )
        self.assertEqual(result["recommended_quantity"], 10)

    def test_missing_moq_defaults_to_zero(self):
        result = self.logic.analyse_inventory(
            make_record(stock=10, usage=5, lead=1, moq=None), self.assessment
        )
        self.assertEqual(result["recommended_quantity"], 10)

    def test_no_reorder_when_stock_is_above_reorder_point(self):
        result = self.logic.analyse_inventory(make_record(stock=100), self.assessment)
        self.assertEqual(result["recommended_quantity"], 0)
        self.assertEqual(result["action"], "MONITOR")

    def test_reorder_triggers_exactly_at_reorder_point(self):
        result = self.logic.analyse_inventory(make_record(stock=32), self.assessment)
        self.assertNotEqual(result["action"], "MONITOR")
        self.assertGreater(result["recommended_quantity"], 0)

    def test_budget_escalation_flags_without_changing_quantity(self):
        result = self.logic.analyse_inventory(make_record(budget=1000), self.assessment)
        self.assertTrue(result["budget_escalation"])
        self.assertEqual(result["estimated_cost"], 1050)
        self.assertEqual(result["recommended_quantity"], 30)
        self.assertEqual(result["action"], "URGENT REORDER")

    def test_cost_equal_to_budget_is_not_escalated(self):
        result = self.logic.analyse_inventory(make_record(budget=1050), self.assessment)
        self.assertFalse(result["budget_escalation"])


class TestSafetyStock(LogicManagerTestCase):
    def test_base_safety_stock_is_one_week_of_usage(self):
        self.assertEqual(self.logic.calculate_safety_stock(10, self.assessment), 10)

    def test_increasing_demand_adds_half_a_week(self):
        assessment = make_assessment(trend="increasing")
        self.assertEqual(self.logic.calculate_safety_stock(10, assessment), 15)

    def test_high_supply_risk_adds_half_a_week(self):
        assessment = make_assessment(supply="high")
        self.assertEqual(self.logic.calculate_safety_stock(10, assessment), 15)

    def test_high_operational_importance_adds_half_a_week(self):
        assessment = make_assessment(importance="high")
        self.assertEqual(self.logic.calculate_safety_stock(10, assessment), 15)

    def test_all_three_additions_combine(self):
        assessment = make_assessment("increasing", "high", "high")
        self.assertEqual(self.logic.calculate_safety_stock(10, assessment), 25)

    def test_safety_stock_is_rounded_up(self):
        assessment = make_assessment(trend="increasing")
        self.assertEqual(self.logic.calculate_safety_stock(3, assessment), 5)  # 4.5 -> 5

    def test_risk_factors_raise_the_reorder_point(self):
        base = self.logic.analyse_inventory(make_record(), self.assessment)
        risky = self.logic.analyse_inventory(
            make_record(), make_assessment("increasing", "high", "high")
        )
        self.assertGreater(risky["reorder_point"], base["reorder_point"])
        self.assertGreater(risky["recommended_quantity"], base["recommended_quantity"])


class TestValidation(LogicManagerTestCase):
    def test_invalid_assessment_value_is_rejected(self):
        bad = make_assessment(trend="sideways")
        with self.assertRaises(ValueError):
            self.logic.analyse_inventory(make_record(), bad)

    def test_negative_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.logic.analyse_inventory(make_record(stock=-1), self.assessment)

    def test_missing_unit_cost_is_rejected_when_extended_features_on(self):
        with self.assertRaises(ValueError):
            self.logic.analyse_inventory(make_record(unit_cost=None), self.assessment)


class TestSimulation(LogicManagerTestCase):
    def setUp(self):
        super().setUp()
        self.record = make_record()
        self.baseline = self.logic.analyse_inventory(self.record, self.assessment)

    def test_simulation_with_increased_weekly_usage(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 12, 3)
        # safety 12, reorder point 48, target 72, shortage 54
        self.assertEqual(result["safety_stock"], 12)
        self.assertEqual(result["reorder_point"], 48)
        self.assertEqual(result["recommended_quantity"], 54)
        self.assertEqual(result["estimated_cost"], 1890)
        self.assertFalse(result["budget_escalation"])

    def test_simulation_with_increased_lead_time(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 8, 5)
        # reorder point 8*5+8 = 48, target 64, shortage 46
        self.assertEqual(result["reorder_point"], 48)
        self.assertEqual(result["recommended_quantity"], 46)
        self.assertEqual(result["estimated_cost"], 1610)

    def test_simulation_with_both_values_changed(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 12, 5)
        # safety 12, reorder point 72, target 96, shortage 78
        self.assertEqual(result["reorder_point"], 72)
        self.assertEqual(result["recommended_quantity"], 78)
        self.assertEqual(result["estimated_cost"], 2730)
        self.assertTrue(result["budget_escalation"])

    def test_simulation_result_has_same_structure_as_analysis(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 12, 5)
        self.assertEqual(set(result), set(self.baseline))

    def test_simulation_with_unchanged_values_matches_baseline(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 8, 3)
        self.assertEqual(result, self.baseline)

    def test_comparison_against_original_analysis(self):
        simulated = self.logic.simulate_procurement(self.record, self.assessment, 12, 5)
        self.assertEqual(self.baseline["recommended_quantity"], 30)
        self.assertGreater(
            simulated["recommended_quantity"], self.baseline["recommended_quantity"]
        )
        self.assertGreater(simulated["reorder_point"], self.baseline["reorder_point"])
        self.assertGreater(simulated["estimated_cost"], self.baseline["estimated_cost"])
        self.assertNotEqual(simulated["budget_escalation"], self.baseline["budget_escalation"])

    def test_original_inventory_and_assessment_are_unchanged(self):
        before_record = vars(self.record).copy()
        before_assessment = vars(self.assessment).copy()
        self.logic.simulate_procurement(self.record, self.assessment, 12, 5)
        self.assertEqual(vars(self.record), before_record)
        self.assertEqual(vars(self.assessment), before_assessment)
        self.assertEqual(self.record.weekly_usage, 8)
        self.assertEqual(self.record.lead_time_weeks, 3)
        # Re-running the baseline gives the same answer as before the simulation.
        self.assertEqual(
            self.logic.analyse_inventory(self.record, self.assessment), self.baseline
        )

    def test_simulation_with_zero_weekly_usage(self):
        result = self.logic.simulate_procurement(self.record, self.assessment, 0, 3)
        self.assertEqual(result["recommended_quantity"], 0)
        self.assertEqual(result["action"], "MONITOR")
        self.assertIsNone(result["stock_coverage"])

    def test_simulation_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            self.logic.simulate_procurement(self.record, self.assessment, -1, 3)
        with self.assertRaises(ValueError):
            self.logic.simulate_procurement(self.record, self.assessment, 8, -2)


if __name__ == "__main__":
    unittest.main()