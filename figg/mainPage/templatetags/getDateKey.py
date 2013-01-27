from django.template import Library
from mainPage import event_calculation

register = Library()

@register.filter
def get_date_key( value ):
    """
      Filter - returns the datekey as defined by the datekey func in
      event_claculation
    """

    return event_calculation.get_date_key( value )
