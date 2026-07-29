"""
Project-wide monetary helpers.

- parse_money / clean_decimal: strip thousand-separator commas before DB/math
- format_money: display with commas and 2 decimal places
"""
from __future__ import annotations

import decimal
import re
from typing import Any, Optional, Union

NumberLike = Union[str, int, float, decimal.Decimal, None]

_TWO_DP = decimal.Decimal("0.01")
# 1,234 or 1,234.56 or -12.5 (after optional currency symbols)
_MONEY_WITH_COMMA = re.compile(
    r"^[^\d\-]*-?\d{1,3}(,\d{3})+(\.\d+)?[^\d]*$"
)
_PLAIN_NUMBER = re.compile(r"^-?\d+(\.\d+)?$")


def strip_money_commas(value: Any) -> Any:
    """
    If *value* is a string that looks like a number with thousand separators,
    return the same number without commas. Otherwise return *value* unchanged.
    Safe for names, addresses, and other non-numeric text containing commas.
    """
    if value is None:
        return value
    if not isinstance(value, str):
        return value

    raw = value.strip()
    if not raw or "," not in raw:
        return value

    # Keep only leading minus, digits, commas, and one decimal point for the test
    cleaned = (
        raw.replace("₦", "")
        .replace("N", "")
        .replace("$", "")
        .replace("£", "")
        .replace("€", "")
        .replace(" ", "")
        .strip()
    )
    # If after removing commas it is a plain number, accept it
    no_commas = cleaned.replace(",", "")
    if _PLAIN_NUMBER.fullmatch(no_commas):
        return no_commas
    return value


def parse_money(value: NumberLike, default: Optional[decimal.Decimal] = None) -> decimal.Decimal:
    """
    Parse a monetary value that may contain commas / currency symbols.
    Returns Decimal quantized to 2 decimal places.
    """
    if value is None or value == "":
        if default is not None:
            return default
        return decimal.Decimal("0.00")

    if isinstance(value, decimal.Decimal):
        try:
            return value.quantize(_TWO_DP, rounding=decimal.ROUND_HALF_UP)
        except decimal.InvalidOperation:
            return default if default is not None else decimal.Decimal("0.00")

    if isinstance(value, (int, float)):
        try:
            return decimal.Decimal(str(value)).quantize(
                _TWO_DP, rounding=decimal.ROUND_HALF_UP
            )
        except (decimal.InvalidOperation, ValueError):
            return default if default is not None else decimal.Decimal("0.00")

    s = strip_money_commas(str(value).strip())
    if not isinstance(s, str):
        s = str(s)
    s = (
        s.replace("₦", "")
        .replace("$", "")
        .replace("£", "")
        .replace("€", "")
        .replace(" ", "")
        .replace(",", "")
        .strip()
    )
    if s == "" or s == "-":
        return default if default is not None else decimal.Decimal("0.00")

    try:
        return decimal.Decimal(s).quantize(_TWO_DP, rounding=decimal.ROUND_HALF_UP)
    except (decimal.InvalidOperation, ValueError, TypeError):
        if default is not None:
            return default
        return decimal.Decimal("0.00")


# Alias used across sales / purchase modules
clean_decimal = parse_money


def format_money(value: NumberLike, places: int = 2) -> str:
    """
    Format a number for display with thousand separators and fixed decimals.
    e.g. 1234.5 -> '1,234.50'
    """
    if value is None or value == "":
        return f"0.{'0' * places}"

    try:
        if isinstance(value, str):
            num = parse_money(value)
        else:
            num = decimal.Decimal(str(value))
        quant = decimal.Decimal("1." + ("0" * places)) if places else decimal.Decimal("1")
        num = num.quantize(quant, rounding=decimal.ROUND_HALF_UP)
        # Use en_US style commas
        return f"{num:,.{places}f}"
    except (decimal.InvalidOperation, ValueError, TypeError):
        return f"0.{'0' * places}"


def patch_drf_decimal_field() -> None:
    """
    Make DRF DecimalField accept comma-formatted strings (e.g. '1,234.50').
    Safe to call multiple times.
    """
    try:
        from rest_framework import serializers
    except Exception:
        return

    if getattr(serializers.DecimalField, "_afrikbook_comma_patch", False):
        return

    original = serializers.DecimalField.to_internal_value

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = strip_money_commas(data)
        return original(self, data)

    serializers.DecimalField.to_internal_value = to_internal_value
    serializers.DecimalField._afrikbook_comma_patch = True


def sanitize_mapping(data) -> None:
    """
    In-place: strip money commas from every value in a mutable QueryDict / dict.
    For QueryDict, handles multi-value keys (e.g. amount[]).
    """
    if data is None:
        return

    # Django QueryDict
    if hasattr(data, "getlist") and hasattr(data, "setlist"):
        if not getattr(data, "_mutable", True):
            data._mutable = True
        for key in list(data.keys()):
            values = data.getlist(key)
            cleaned = [strip_money_commas(v) for v in values]
            if cleaned != values:
                data.setlist(key, cleaned)
        return

    # Plain dict
    if isinstance(data, dict):
        for key, value in list(data.items()):
            if isinstance(value, list):
                data[key] = [strip_money_commas(v) for v in value]
            else:
                data[key] = strip_money_commas(value)
