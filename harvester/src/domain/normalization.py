import re
from decimal import Decimal, InvalidOperation

PRICE_NOISE_PATTERN = re.compile(r"(?i)\s*(bs\.?|bob|\$us|usd|\$)\s*")
PRICE_DIGITS_PATTERN = re.compile(r"[0-9][0-9.,\s]*")


def parse_bob_price(raw_price: str | None) -> Decimal | None:
    if raw_price is None:
        return None
    cleaned_price = PRICE_NOISE_PATTERN.sub("", raw_price).strip()
    digits_match = PRICE_DIGITS_PATTERN.search(cleaned_price)
    if digits_match is None:
        return None
    number_text = re.sub(r"\s", "", digits_match.group(0)).rstrip(".,")
    last_comma = number_text.rfind(",")
    last_dot = number_text.rfind(".")
    decimal_separator_index = max(last_comma, last_dot)
    has_decimal_part = decimal_separator_index != -1 and len(number_text) - decimal_separator_index - 1 in (1, 2)
    if has_decimal_part:
        integer_part = re.sub(r"[.,]", "", number_text[:decimal_separator_index])
        normalized_number = f"{integer_part}.{number_text[decimal_separator_index + 1 :]}"
    else:
        normalized_number = re.sub(r"[.,]", "", number_text)
    try:
        return Decimal(normalized_number)
    except InvalidOperation:
        return None
