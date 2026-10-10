# AI / business-rule split
#     The AI only judges qualitative context (demand, supply, importance).
#     Quantitative stock signals are NOT supplied by the AI: stock_condition and
#     stockout_risk are derived here from the inventory data (see
#     derive_stock_condition and derive_stockout_risk).
 
# CORE (basic system)
#     Inventory input : current_stock, weekly_usage, lead_time_weeks
#     Optional input  : moq (minimum order quantity; defaults to 0 if absent)
#     AI assessment   : demand_level, demand_trend, supply_risk,
#                       operational_importance, reason
#     Derived here    : stock_condition, stockout_risk
#     Output          : recommended_quantity, priority, action
 
# EXTENDED (disabled by default, set EXTENDED_FEATURES_ENABLED = True)
#     Extra input     : unit_cost, budget
#     Extra output    : stock_coverage, reorder_point, estimated_cost,
#                       budget_escalation
 
# Reorder point and stock coverage are still calculated internally because
# the Core quantity, priority and derived-signal rules depend on them; they are
# simply not returned (and unit_cost / budget are not required) unless the
# Extended flag is switched on.

 
import math
 
# Temporarily disabled for the basic integration.
EXTENDED_FEATURES_ENABLED = False
 
CORE_INPUT_FIELDS = ("current_stock", "weekly_usage", "lead_time_weeks")
 
# Categorical fields the AI must return. "reason" is free text and is validated separately in _validate_assessment().
AI_VALUES = {
    "demand_level": {"low", "medium", "high"},
    "demand_trend": {"stable", "increasing", "decreasing"},
    "supply_risk": {"low", "medium", "high"},
    "operational_importance": {"low", "medium", "high"},
}
 
 
def _number(record, key, *, allow_zero=True):
    # Read a finite, non-negative number from a record.
    value = record.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{key} must be a number")
    if not math.isfinite(value):
        raise ValueError(f"{key} must be a finite number")
    if value < 0 or (not allow_zero and value == 0):
        qualifier = "greater than zero" if not allow_zero else "non-negative"
        raise ValueError(f"{key} must be {qualifier}")
    return float(value)
 
 
def _validate_assessment(assessment):
    # Check the AI assessment schema (stock_condition/stockout_risk removed).
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be a dictionary")
    for field, accepted in AI_VALUES.items():
        value = assessment.get(field)
        if not isinstance(value, str) or value.lower() not in accepted:
            raise ValueError(f"assessment.{field} must be one of {sorted(accepted)}")
    reason = assessment.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("assessment.reason must be a non-empty string")
 
 
def calculate_stock_coverage(current_stock, weekly_usage):
    # Return weeks of stock remaining, or None when usage is zero.
    if weekly_usage == 0:
        return None
    return current_stock / weekly_usage
 
 
def calculate_reorder_point(weekly_usage, lead_time_weeks, safety_stock=None):
    # Reorder point = usage during lead time + safety stock.
    # When no safety stock is supplied, one week of average usage is used.
    
    if safety_stock is None:
        safety_stock = weekly_usage
    return weekly_usage * lead_time_weeks + safety_stock
 
 
def derive_stock_condition(current_stock, weekly_usage, reorder_point, safety_stock):
    # Derive stock condition from the inventory position.
 
    # critical : stock has fallen to or below the safety-stock cushion
    # at_risk  : stock has reached the reorder point (but is above safety stock)
    # healthy  : stock is above the reorder point, or there is no demand
    
    if weekly_usage == 0:
        return "healthy"
    if current_stock <= safety_stock:
        return "critical"
    if current_stock <= reorder_point:
        return "at_risk"
    return "healthy"
 
 
def derive_stockout_risk(coverage_weeks, lead_time_weeks, current_stock, reorder_point):
    # Derive stockout risk from stock timing versus supplier lead time.
 
    # high   : stock will run out before a new order can arrive
    # medium : stock has reached the reorder point
    # low    : stock is above the reorder point, or there is no demand
    
    if coverage_weeks is None:
        return "low"
    if coverage_weeks <= lead_time_weeks:
        return "high"
    if current_stock <= reorder_point:
        return "medium"
    return "low"
 
 
def recommend_order_quantity(current_stock, reorder_point, moq):
    # Order enough to reach the reorder point, subject to supplier MOQ.
    shortage = max(0.0, reorder_point - current_stock)
    return max(shortage, moq) if shortage > 0 else 0.0
 
 
def determine_priority(coverage_weeks, lead_time_weeks, reorder_needed,
                       assessment, stock_condition, stockout_risk):
    # Apply fixed, explainable priority rules.
 
    # Uses AI context (supply_risk, demand_trend), stock_condition and
    # stockout_risk values derived from inventory data.
    
    supply_risk = assessment["supply_risk"].lower()
    trend = assessment["demand_trend"].lower()
 
    if not reorder_needed:
        # Escalate monitoring when the derived signals show a serious risk
        # despite stock still being above the calculated reorder point.
        if stockout_risk == "high" or stock_condition == "critical":
            return "HIGH"
        if supply_risk == "high" or trend == "increasing":
            return "MEDIUM"
        return "LOW"
 
    if (coverage_weeks is not None and coverage_weeks <= lead_time_weeks) or \
            stockout_risk == "high" or stock_condition == "critical":
        return "HIGH"
    if supply_risk in {"medium", "high"} or trend == "increasing" or \
            stock_condition == "at_risk" or stockout_risk == "medium":
        return "MEDIUM"
    return "LOW"
 
 
def analyse_inventory(inventory, assessment, safety_stock=None):
    
    if not isinstance(inventory, dict):
        raise ValueError("inventory must be a dictionary")
    _validate_assessment(assessment)
 
    stock = _number(inventory, "current_stock")
    usage = _number(inventory, "weekly_usage")
    lead_time = _number(inventory, "lead_time_weeks")
    moq = _number(inventory, "moq") if inventory.get("moq") is not None else 0.0
 
    if safety_stock is not None:
        if (isinstance(safety_stock, bool)
                or not isinstance(safety_stock, (int, float))
                or not math.isfinite(safety_stock)
                or safety_stock < 0):
            raise ValueError("safety_stock must be a non-negative number")
        safety_stock = float(safety_stock)
    else:
        safety_stock = usage  # default: one week of average usage
 
    coverage = calculate_stock_coverage(stock, usage)
    reorder_point = calculate_reorder_point(usage, lead_time, safety_stock)
    order_quantity = recommend_order_quantity(stock, reorder_point, moq)
    reorder_needed = order_quantity > 0

    stock_condition = derive_stock_condition(stock, usage, reorder_point, safety_stock)
    stockout_risk = derive_stockout_risk(coverage, lead_time, stock, reorder_point)
 
    priority = determine_priority(coverage, lead_time, reorder_needed,
                                  assessment, stock_condition, stockout_risk)
    if not reorder_needed:
        action = "MONITOR"
    elif priority == "HIGH":
        action = "URGENT REORDER"
    else:
        action = "REORDER"
 
    result = {
        "recommended_quantity": int(order_quantity),
        "priority": priority,
        "action": action,
    }
 
    if EXTENDED_FEATURES_ENABLED:
        unit_cost = _number(inventory, "unit_cost")
        budget = _number(inventory, "budget")
        estimated_cost = order_quantity * unit_cost
        result.update({
            "stock_coverage": round(coverage, 2) if coverage is not None else None,
            "reorder_point": round(reorder_point, 2),
            "estimated_cost": round(estimated_cost, 2),
            "budget_escalation": estimated_cost > budget,
        })
 
    return result