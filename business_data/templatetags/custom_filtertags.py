from django import template

register = template.Library()

@register.filter
def pretty_label(value):
    """Replace underscores with spaces and capitalize each word."""
    return str(value).replace('_', ' ').title()