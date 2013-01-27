from django.template import Library

register = Library()

@register.filter
def get_key( arg, value):

    if not arg:
        return False

    if value in arg:
        return arg[value]
    else:
        return False
