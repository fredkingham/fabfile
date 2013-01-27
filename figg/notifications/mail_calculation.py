from mainPage.models import AttendingStatus, InvitedStatus
from notifications.models import Notification, PostedNotification 
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from datetime import datetime
from notifications import notification_calculation, NotificationException
from notifications import FROM_EMAIL
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def notify(notification_id):
    notification = Notification.objects.get(id = notification_id)
    context = notification_calculation.get_notification_context(notification)

    logger.info("processing context of %s" % context)

    if context.type not in Notification.NOTIFICATION_MAP.values():
        raise NotificationException("unknown type passed in %s" % context.type)

    send_notification(context)

    db_args = {
            "notification_type": PostedNotification.NOTIFICATION,
            "args": notification_id,
            "processed": True,
            "receiver": context.email
            }


    postedNotification = PostedNotification(**db_args)
    postedNotification.save()

def send_notification(context):
    to_email = getattr(context, "email", None)
    if not to_email:
        to_email = User.objects.get(username = context.user).email 

    to_emails = [to_email]
    from_email = FROM_EMAIL
    context_map = {'context': context, "MEDIA_URL": settings.MEDIA_URL, "STATIC_URL": settings.STATIC_URL }
    context_map["HOME"] = settings.HOME
    d = Context(context_map)
    plaintext = get_template('%s.txt' % context.get_template())
    html = get_template('%s.html' % context.get_template())
    text_content = plaintext.render(d)
    msg = EmailMultiAlternatives(context.msg(), text_content, from_email, to_emails)
    #html_content = html.render(d)
    #msg.attach_alternative(html_content, "text/html")
    logger.info("sending an email of %s to %s" % (context.type, to_emails))
    msg.send()


def test_send():
    potential = Notification.objects.filter(notification_type = Notification.INVITE)
    potential = potential.filter(user__username = "fredkingham")[0]
    notify(potential.id)


