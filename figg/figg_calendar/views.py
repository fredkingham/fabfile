from figg_calendar import tracking_calculation, forms, profile_calculation
from django.http import Http404, HttpResponse

import logging
logger = logging.getLogger(__name__)

from common import complex_encoder
encoder = complex_encoder.Encoder()

def select(request):
    if request.user.is_authenticated() and request.method == 'POST':
        form = forms.SelectCalendarForm(request.POST, request.FILES)
        if form.is_valid():
            args = form.cleaned_data
            args["user"] = request.user
            print "args are %s" % args
            tracking_calculation.select(**args)
            return HttpResponse(encoder.encode(0), mimetype='application/json')
        else:
            print "form errors %s" % form.errors
            logger.error("select errors %s" % form.errors)

    return HttpResponse(encoder.encode(1), mimetype='application/json')


def remove(request):
    if request.user.is_authenticated():
        form = forms.TrackingQueryForm(request.POST, request.FILES)
        if form.is_valid():
            args = form.cleaned_data
            args["user"] = request.user
            tracking_calculation.remove(**args)
            return HttpResponse(encoder.encode(0), mimetype='application/json')
    else:
        return HttpResponse(encoder.encode(1), mimetype='application/json')

def get_trackers(request):
    form = forms.TrackingQueryForm(request.GET, request.FILES)
    if form.is_valid():
        args = form.cleaned_data
        if request.user.is_authenticated():
            args["user"] = request.user

        return HttpResponse(encoder.encode(tracking_calculation.get_trackers(**args)), mimetype='application/json')
    else:
        logger.error("get trackers failed with %s" % form.errors)
        return HttpResponse(encoder.encode(1), mimetype='application/json')

def get_tags(request):
    form = forms.RelatedTags(request.GET)

    if form.is_valid():
        args = form.cleaned_data
        print "hera %s" % args
        if request.user.is_authenticated():
            args["user"] = request.user

        return HttpResponse(encoder.encode(tracking_calculation.get_related_tags(**args)), mimetype='application/json')


    #go go go
    pass

def get_selected(request):
    """ returns all the user details of of the selected """
    if request.user.is_authenticated() and request.method == 'GET':
        return tracking_calculation.get_selected(request.user)


def tracking(request):
    """ returns everything that the user has selected """
    if request.user.is_authenticated() and request.method == 'GET':
        form = forms.Tracking(request.GET)
        if form.is_valid():
            other_user = form.cleaned_data["cal"]
            if not other_user:
                other_user = request.user
            return HttpResponse(encoder.encode(tracking_calculation.get_tracking(other_user, request.user)), mimetype='application/json')
        else:
            logger.error("tracking invalid with %s" % form.errors)

    return HttpResponse(encoder.encode(1), mimetype='application/json')

def get_profile(request):
    form = forms.TrackingQueryForm(request.GET)

    if form.is_valid():
        args = form.cleaned_data
        if request.user.is_authenticated():
            args["user"] = request.user

        return HttpResponse(encoder.encode(profile_calculation.get_profile(**args)), mimetype='application/json')

    raise Http404








