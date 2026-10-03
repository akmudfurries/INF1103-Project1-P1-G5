"""Deterministic procurement rules for the AI Inventory & Procurement Advisor.

This module accepts a validated AI assessment; it does not call the AI API or
provide a fallback assessment. Keep AI/schema validation in validation.py.

Expected inventory keys:
    current_stock, weekly_usage, lead_time_weeks, minimum_order_quantity,
    unit_cost, available_budget

Expected AI keys:
    demand_level, demand_trend, stock_condition, stockout_risk, supply_risk
"""


AI_VALUES = {
    "demand_level": {"low", "medium", "high"},
    "demand_trend": {"stable", "increasing", "decreasing"},
    "stock_condition": {"healthy", "at_risk", "critical"},
    "stockout_risk": {"low", "medium", "high"},
    "supply_risk": {"low", "medium", "high"},
}


def _number(record, key, *, allow_zero=True):
    """Read a finite, non-negative number from a record."""
    value = record.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    if value < 0 or (not allow_zero and value == 0):
        qualifier = "greater than zero" if not allow_zero else "non-negative"
        raise ValueError(f"{key} must be {qualifier}")
    return float(value)


def _validate_assessment(assessment):
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be a dictionary")
    for field, accepted in AI_VALUES.items():
        value = assessment.get(field)
        if not isinstance(value, str) or value.lower() not in accepted:
            raise ValueError(f"assessment.{field} must be one of {sorted(accepted)}")


def calculate_stock_coverage(current_stock, weekly_usage):
    """Return weeks of stock remaining, or None when usage is zero."""
    if weekly_usage == 0:
        return None
    return current_stock / weekly_usage


def calculate_reorder_point(weekly_usage, lead_time_weeks, safety_stock=None):
    """Reorder point = usage during lead time + safety stock.

    When no safety stock is supplied, one week of average usage is used. This
    matches the report's worked example (15 units per week -> 15 safety units).
    """
    if safety_stock is None:
        safety_stock = weekly_usage
    return weekly_usage * lead_time_weeks + safety_stock


def recommend_order_quantity(current_stock, reorder_point, minimum_order_quantity):
    """Order enough to reach the reorder point, subject to supplier MOQ."""
    shortage = max(0.0, reorder_point - current_stock)
    return max(shortage, minimum_order_quantity) if shortage > 0 else 0.0


def determine_priority(coverage_weeks, lead_time_weeks, reorder_needed, assessment):
    """Apply fixed, explainable priority rules using inventory and validated AI."""
    stockout_risk = assessment["stockout_risk"].lower()
    supply_risk = assessment["supply_risk"].lower()
    trend = assessment["demand_trend"].lower()
    condition = assessment["stock_condition"].lower()

    if not reorder_needed:
        # Escalate monitoring when AI highlights a serious risk despite stock
        # still being above the calculated reorder point.
        if stockout_risk == "high" or condition == "critical":
            return "HIGH"
        if supply_risk == "high" or trend == "increasing":
            return "MEDIUM"
        return "LOW"

    if (coverage_weeks is not None and coverage_weeks <= lead_time_weeks) or \
            stockout_risk == "high" or condition == "critical":
        return "HIGH"
    if supply_risk in {"medium", "high"} or trend == "increasing" or \
            condition == "at_risk" or stockout_risk == "medium":
        return "MEDIUM"
    return "LOW"


def analyse_inventory(inventory, assessment, safety_stock=None):
    """Return a procurement recommendation from inventory and validated AI data.

    ``assessment`` must already have passed the schema checks in validation.py.
    A ValueError is raised for missing/invalid input rather than guessing.
    """
    if not isinstance(inventory, dict):
        raise ValueError("inventory must be a dictionary")
    _validate_assessment(assessment)

    stock = _number(inventory, "current_stock")
    usage = _number(inventory, "weekly_usage")
    lead_time = _number(inventory, "lead_time_weeks")
    moq = _number(inventory, "minimum_order_quantity")
    unit_cost = _number(inventory, "unit_cost")
    budget = _number(inventory, "available_budget")
    if safety_stock is not None:
        if isinstance(safety_stock, bool) or not isinstance(safety_stock, (int, float)) or safety_stock < 0:
            raise ValueError("safety_stock must be a non-negative number")
        safety_stock = float(safety_stock)

    coverage = calculate_stock_coverage(stock, usage)
    reorder_point = calculate_reorder_point(usage, lead_time, safety_stock)
    order_quantity = recommend_order_quantity(stock, reorder_point, moq)
    reorder_needed = stock <= reorder_point
    # If no order is required, do not impose an MOQ on a zero shortage.
    if not reorder_needed:
        order_quantity = 0.0

    estimated_cost = order_quantity * unit_cost
    priority = determine_priority(coverage, lead_time, reorder_needed, assessment)
    if order_quantity == 0:
        action = "MONITOR"
    elif priority == "HIGH":
        action = "URGENT REORDER"
    else:
        action = "REORDER"

    return {
        "stock_coverage_weeks": round(coverage, 2) if coverage is not None else None,
        "reorder_point": round(reorder_point, 2),
        "reorder_needed": reorder_needed,
        "recommended_order_quantity": round(order_quantity, 2),
        "estimated_cost": round(estimated_cost, 2),
        "available_budget": round(budget, 2),
        "budget_escalation_required": estimated_cost > budget,
        "priority": priority,
        "action": action,
        "reason": (
            "Stock is at or below the reorder point."
            if reorder_needed else "Stock is above the reorder point."
        ),
    }
