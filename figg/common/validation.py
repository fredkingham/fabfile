from django.utils.html import escape
from django.core import validators
from django.core.exceptions import ValidationError

def safe_get(request, field):
    if request.get(field):
        return escape(request.get(field))
    else:
        return None

def validate_email(email):
    try:
        validators.validate_email( email )
        return True
    except ValidationError:
        return False


