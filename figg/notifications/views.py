from django.template.loader import get_template
from django.template import RequestContext
from notifications.models import LastCheckedNotification, Notification
from notifications import notification_calculation
from datetime import datetime, date
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from figg_calendar import cal_calculation
from common import complex_encoder

def read_notification(request):
    '''returns a map of the last 10 notifications and the times along with the
    time of the most recent unchecked event, if included this will only
    includes notes after a certain notification'''

    if request.user.is_authenticated():
        if request.method == 'POST':
            last_checked_all = LastCheckedNotification.objects.filter(user = request.user)

            last_id = request.POST.get("id")

            if not last_checked_all:
                last_check_notification = LastCheckedNotification(user = request.user, checked = datetime.utcnow())
                last_check_notification.save()
                return HttpResponse(simplejson.dumps([]), mimetype='application/json')
            else:
                last_checked = last_checked_all[0]
                encoder = complex_encoder.Encoder()
                notifications = notification_calculation.get_notifications(request.user, last_checked.checked, last_id)
                last_checked.checked = datetime.utcnow()
                last_checked.save()
                return HttpResponse(encoder.encode(notifications), mimetype='application/json')

    return HttpResponse(simplejson.dumps(0), mimetype='application/json')


def updates(request):
    '''returns a page for all the users updates'''
    if request.method == 'GET' and request.user.is_authenticated():
        details = cal_calculation.get_person_details(request.user)
        t = get_template('index.html')
        page_details = {"start_date": date.today()}
        html = t.render(RequestContext(request, {"details": details, "page_details": page_details}))
        return HttpResponse(html)
    else:
        return HttpResponseRedirect("/")

def show_email(request):
    ''' this is a dev method to show html emails for quick editting '''
    potential = Notification.objects.filter(notification_type = Notification.COMMENT)[0]
    context = notification_calculation.get_notification_context(potential)
    t = get_template('%s.html' % context.get_template())
    html = t.render(RequestContext(request, {'context': context}))
    return HttpResponse(html)
    

