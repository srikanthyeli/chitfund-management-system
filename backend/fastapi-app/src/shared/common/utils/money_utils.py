from decimal import Decimal

def safe_decimal(value: any, default: Decimal = Decimal('0.00')) -> Decimal:
    """Safely converts a value to Decimal."""
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default
