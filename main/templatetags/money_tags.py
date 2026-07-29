"""
Template filters for monetary display.

Loaded globally via TEMPLATES OPTIONS builtins so every template can use:

    {{ value|money }}
    {{ value|money:0 }}
"""
from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

from main.money import format_money, parse_money

register = template.Library()


@register.filter(name="money")
def money_filter(value, places=2):
    """
    Format a number with thousand separators and fixed decimals.
    Example: 12345.5 -> 12,345.50
    """
    try:
        places = int(places)
    except (TypeError, ValueError):
        places = 2
    return format_money(value, places=places)


@register.filter(name="money_plain")
def money_plain_filter(value, places=2):
    """
    Format without commas (for hidden inputs that must stay numeric).
    """
    try:
        places = int(places)
    except (TypeError, ValueError):
        places = 2
    num = parse_money(value)
    quant = "1." + ("0" * places) if places else "1"
    import decimal
    num = num.quantize(decimal.Decimal(quant), rounding=decimal.ROUND_HALF_UP)
    return f"{num:.{places}f}"
