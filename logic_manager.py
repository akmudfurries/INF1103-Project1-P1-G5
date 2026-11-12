# LogicManager: procurement business rules (Phase 2, OOP refactor).
#
# AI / business-rule split
#     The AI only judges qualitative context (demand, supply, importance).
#     Quantitative stock signals are NOT supplied by the AI: stock_condition and
#     stockout_risk are derived here from the inventory data.
#
# Inputs : InventoryRecord (current_stock, weekly_usage, lead_time_weeks, optional
#          moq, unit_cost, budget) and AIAssessment.
# Output : analysis result dictionary (see analyse_inventory).
#
# EXTENDED_FEATURES_ENABLED keeps its existing tested behaviour:
#     True  -> safety stock uses the AI-based safety weeks, unit_cost and budget
#              are required, and the cost / budget fields are returned.
#     False -> safety stock is one week of usage and only the core fields are
#              returned.
# Its value is set for integration and must not be changed without instruction.

import math
from dataclasses import replace
from typing import Any

from config import ALLOWED_ANSWERS
from models import AIAssessment, InventoryRecord

# Switched on for integration.
EXTENDED_FEATURES_ENABLED: bool = True


class LogicManager:
    """Applies the fixed, explainable procurement rules to inventory data."""

    # ---------- validation helpers ----------

    @staticmethod
    def _check_number(value: Any, name: str) -> float:
        # Return value as a finite, non-negative float, or raise ValueError.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")
        return float(value)

    def _validate_assessment(self, assessment: AIAssessment) -> None:
        # Check the AI assessment values (stock signals are not part of it).
        if assessment is None:
            raise ValueError("assessment is required")
        for field, accepted in ALLOWED_ANSWERS.items():
            value = getattr(assessment, field, None)
            if not isinstance(value, str) or value.lower() not in accepted:
                raise ValueError(
                    f"assessment.{field} must be one of {sorted(accepted)}"
                )
        reason = getattr(assessment, "reason", None)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("assessment.reason must be a non-empty string")

    # ---------- calculations ----------

    def calculate_stock_coverage(self, stock: float, usage: float) -> float | None:
        # Weeks of stock remaining, or None when usage is zero.
        if usage == 0:
            return None
        return stock / usage

    def _safety_weeks(self, assessment: AIAssessment) -> float:
        # One base week, plus 0.5 week for each risk factor in the AI's view.
        weeks = 1.0
        if assessment.demand_trend.lower() == "increasing":
            weeks += 0.5
        if assessment.supply_risk.lower() == "high":
            weeks += 0.5
        if assessment.operational_importance.lower() == "high":
            weeks += 0.5
        return weeks

    def calculate_safety_stock(
        self, weekly_usage: float, assessment: AIAssessment
    ) -> float:
        # Ceiling of weekly usage x safety weeks (one week of usage when the
        # extended features are switched off).
        if not EXTENDED_FEATURES_ENABLED:
            return float(weekly_usage)
        return float(math.ceil(weekly_usage * self._safety_weeks(assessment)))

    def calculate_reorder_point(
        self, weekly_usage: float, lead_time: float, safety_stock: float
    ) -> float:
        # Usage during the lead time plus safety stock.
        return weekly_usage * lead_time + safety_stock

    def derive_stock_condition(
        self,
        current_stock: float,
        reorder_point: float,
        safety_stock: float = 0.0,
        weekly_usage: float | None = None,
    ) -> str:
        # critical : stock is at or below the safety-stock cushion
        # at_risk  : stock has reached the reorder point (above safety stock)
        # healthy  : stock is above the reorder point, or there is no demand
        if weekly_usage is not None and weekly_usage == 0:
            return "healthy"
        if current_stock <= safety_stock:
            return "critical"
        if current_stock <= reorder_point:
            return "at_risk"
        return "healthy"

    def derive_stockout_risk(
        self,
        stock_coverage: float | None,
        lead_time_weeks: float,
        current_stock: float | None = None,
        reorder_point: float | None = None,
    ) -> str:
        # high   : stock will run out before a new order can arrive
        # medium : stock has reached the reorder point
        # low    : stock is above the reorder point, or there is no demand
        if stock_coverage is None:
            return "low"
        if stock_coverage <= lead_time_weeks:
            return "high"
        if (
            current_stock is not None
            and reorder_point is not None
            and current_stock <= reorder_point
        ):
            return "medium"
        return "low"

    def recommend_order_quantity(
        self,
        current_stock: float,
        reorder_point: float,
        weekly_usage: float,
        moq: float,
    ) -> int:
        # Order up to the target stock (reorder point + two weeks of usage),
        # but never less than the supplier MOQ.
        target_stock = reorder_point + weekly_usage * 2
        shortage = max(0.0, target_stock - current_stock)
        if shortage <= 0:
            return 0
        return math.ceil(max(shortage, moq))

    def determine_priority(
        self,
        stockout_risk: str,
        assessment: AIAssessment,
        reorder_needed: bool = True,
        stock_condition: str = "healthy",
    ) -> str:
        # Fixed, explainable priority rules.
        supply_risk = assessment.supply_risk.lower()
        trend = assessment.demand_trend.lower()

        if not reorder_needed:
            # Escalate monitoring when the derived signals show a serious risk
            # even though stock is still above the reorder point.
            if stockout_risk == "high" or stock_condition == "critical":
                return "HIGH"
            if supply_risk == "high" or trend == "increasing":
                return "MEDIUM"
            return "LOW"

        if stockout_risk == "high" or stock_condition == "critical":
            return "HIGH"
        if (
            supply_risk in {"medium", "high"}
            or trend == "increasing"
            or stock_condition == "at_risk"
            or stockout_risk == "medium"
        ):
            return "MEDIUM"
        return "LOW"

    # ---------- analysis ----------

    def analyse_inventory(
        self,
        inventory: InventoryRecord,
        assessment: AIAssessment,
        safety_stock: float | None = None,
    ) -> dict[str, Any]:
        self._validate_assessment(assessment)

        stock = self._check_number(getattr(inventory, "current_stock", None), "current_stock")
        usage = self._check_number(getattr(inventory, "weekly_usage", None), "weekly_usage")
        lead_time = self._check_number(
            getattr(inventory, "lead_time_weeks", None), "lead_time_weeks"
        )
        raw_moq = getattr(inventory, "moq", None)
        moq = self._check_number(raw_moq, "moq") if raw_moq is not None else 0.0

        if safety_stock is not None:
            safety_stock = self._check_number(safety_stock, "safety_stock")
        else:
            safety_stock = self.calculate_safety_stock(usage, assessment)

        coverage = self.calculate_stock_coverage(stock, usage)
        reorder_point = self.calculate_reorder_point(usage, lead_time, safety_stock)

        # Zero usage never triggers a reorder.
        reorder_needed = usage > 0 and stock <= reorder_point

        if reorder_needed:
            order_quantity = self.recommend_order_quantity(
                stock, reorder_point, usage, moq
            )
        else:
            order_quantity = 0

        stock_condition = self.derive_stock_condition(
            stock, reorder_point, safety_stock, usage
        )
        stockout_risk = self.derive_stockout_risk(
            coverage, lead_time, stock, reorder_point
        )
        priority = self.determine_priority(
            stockout_risk, assessment, reorder_needed, stock_condition
        )

        if not reorder_needed:
            action = "MONITOR"
        elif priority == "HIGH":
            action = "URGENT REORDER"
        else:
            action = "REORDER"

        result: dict[str, Any] = {
            "recommended_quantity": int(order_quantity),
            "priority": priority,
            "action": action,
            "stock_condition": stock_condition,
            "stockout_risk": stockout_risk,
        }

        if EXTENDED_FEATURES_ENABLED:
            unit_cost = self._check_number(getattr(inventory, "unit_cost", None), "unit_cost")
            budget = self._check_number(getattr(inventory, "budget", None), "budget")
            estimated_cost = order_quantity * unit_cost
            result.update(
                {
                    "stock_coverage": (
                        round(coverage, 2) if coverage is not None else None
                    ),
                    "reorder_point": math.ceil(reorder_point),
                    "safety_stock": round(safety_stock, 2),
                    "estimated_cost": round(estimated_cost, 2),
                    "budget": round(budget, 2),
                    # Flag for human review only: quantity is never changed.
                    "budget_escalation": estimated_cost > budget,
                }
            )

        return result

    def simulate_procurement(
        self,
        inventory: InventoryRecord,
        assessment: AIAssessment,
        simulated_usage: float,
        simulated_lead_time: float,
    ) -> dict[str, Any]:
        # What-if analysis: same rules, alternative usage and lead time.
        # Works on a temporary copy, so the original InventoryRecord and
        # AIAssessment are never modified, and nothing is saved.
        usage = self._check_number(simulated_usage, "simulated_usage")
        lead_time = self._check_number(simulated_lead_time, "simulated_lead_time")
        scenario = replace(inventory, weekly_usage=usage, lead_time_weeks=lead_time)
        return self.analyse_inventory(scenario, assessment)