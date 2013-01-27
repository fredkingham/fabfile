from django.template import Library

register = Library()

@register.filter
def modulus( arg, value ):
    if not arg:
        return False
    return arg % value == 0
