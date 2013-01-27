from mainPage.models import AttendingStatus
from datetime import date, timedelta
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)
from mainPage.event_holder import EventHolderByStatus
from notification_types import EarlyNotification
import mail_calculation
NOTIFICATION_TYPE = "early_notification"


def get_event_structs(status_ids, user):
    event_holder = EventHolderByStatus(status_ids, user)
    event_holder.populate()
    return event_holder.events[0]

def send_early_notifications():
# values... user email, user first name, username
# status so we can pass it to the status holder

    tomorrow = date.today() + timedelta(1)
    query = AttendingStatus.objects.filter(event__date = tomorrow)
    query = query.filter(Q(status = AttendingStatus.ACCEPTED) | Q(status = AttendingStatus.ADDED))
    results = query.values("user__username", "user__first_name", "user__email", "id", "user__id")

    for result in results:
        event = get_event_structs([result["id"]], result["user__id"])
        args = [event, result["user__username"], result["user__first_name"], result["user__email"], NOTIFICATION_TYPE]
        early_notification = EarlyNotification(*args)
        logger.info("sending an email to %s with %s for %s" % ( early_notification.first_name, early_notification.email, early_notification.event.title))
        mail_calculation.send_notification(early_notification)


        




    


    





