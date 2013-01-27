from django.http import HttpResponseRedirect
from mainPage.models import ChosenFew
from twitter import email_confirmation

def authenticated(function):
    def validate_user(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/l/starter")
        if not ChosenFew.objects.filter(user = request.user.username).exists():
            return HttpResponseRedirect("/l/starter")
        if request.user.is_superuser:
            return HttpResponseRedirect("/l/starter")
        if not email_confirmation.email_valid(request.user):
            return HttpResponseRedirect("/d/email_request/")

        return function(request, *args, **kwargs)

    return validate_user

def one_of_the_chosen_few(function):
    def validate_user(request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("/l/starter")
        if not ChosenFew.objects.filter(user = request.user.username).exists():
            return HttpResponseRedirect("/l/starter")
        return function(request, *args, **kwargs)

    return validate_user
