from datetime import datetime


def validate_date(date_str):
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return True, parsed.strftime("%Y-%m-%d")
    except ValueError:
        return False, None


def validate_price(price_str):
    if not price_str.isdigit():
        return False, None

    price = int(price_str)

    if price < 0:
        return False, None

    return True, str(price)
