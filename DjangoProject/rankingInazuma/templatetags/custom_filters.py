from django import template

register = template.Library()

@register.filter(name='strip')
def strip(value):
    """Elimina espacios en blanco al inicio y al final de una cadena."""
    if isinstance(value, str):
        return value.strip()
    return value