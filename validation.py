def validate_positive_number(value_str, allow_float=False):
    # validates that the input string represents a non negative number 
    try:
        num = float(value_str) if allow_float else int(value_str)
        if num < 0:
            return False, "Value cannot be negative."
        return True, num
    except ValueError:
        expected_type = "a decimal number" if allow_float else "a whole number"
        return False, f"Invalid input. Please enter {expected_type}."

def validate_inventory_fields(item, category, stock, usage, lead_time, moq, cost, budget, notes):
    # validates all form fields collected from user CLI prompt n gather error msg into a list

    errors = []

    # text field check
    if not item.strip():
        errors.append("Item name is required.")
    if not category.strip():
        errors.append("Category is required.")
    if not notes.strip():
        errors.append("Operational notes are required.")

    # Numeric field checks
    numeric_checks = [
        ("Current Stock", stock, False),
        ("Average Weekly Usage", usage, False),
        ("Supplier Lead Time", lead_time, False),
        ("Minimum Order Quantity", moq, False),
        ("Unit Cost", cost, True),
        ("Available Budget", budget, True),
    ]

    parsed_values = {}
    for label, val_str, is_float in numeric_checks:
        is_valid, result = validate_positive_number(val_str, allow_float=is_float)
        if not is_valid:
            errors.append(f"{label}: {result}")
        else:
            parsed_values[label] = result

    if errors:
        return False, errors, None

    return True, [], parsed_values


