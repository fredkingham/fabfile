from django.template import Library
from mainPage import event

register = Library()

@register.filter
def get_date_key( value ):
    """
      Filter - returns the datekey as defined by the datekey func in
      event_claculation
    """

    return event.date_translator( value )
