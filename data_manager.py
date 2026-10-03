


def build_inventory_record(
    item_id,
    item_name,
    current_stock,
    weekly_usage,
    lead_time_weeks,
    operational_notes
):
    record = {
        "item_id": item_id,
        "item_name": item_name,
        "current_stock": current_stock,
        "weekly_usage": weekly_usage,
        "lead_time_weeks": lead_time_weeks,
        "operational_notes": operational_notes
    }

    return record