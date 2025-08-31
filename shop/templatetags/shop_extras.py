from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    if value is None:
        return []
    return [s for s in str(value).split(delimiter) if s]

@register.filter
def trim(value):
    if value is None:
        return ''
    return str(value).strip()
