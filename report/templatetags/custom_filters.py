from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg


@register.filter(name="money")
def money(value, places=2):
    """Display money with commas; prefer main.money when available."""
    try:
        from main.money import format_money
        return format_money(value, places=int(places))
    except Exception:
        try:
            from django.contrib.humanize.templatetags.humanize import intcomma
            from django.template.defaultfilters import floatformat
            return intcomma(floatformat(value, int(places)))
        except Exception:
            return value