from datetime import datetime, timedelta
from mainPage.models import Invited_Status
from standalone.sendNotification import invite

def check_invites():
    """ look at all events that should have been sent in the last week send 
        any that haven't been sent """

    raw_query = '''select * from mainPage_InvitedStatus where id not in
    (
        select invited_status_id from standalone_sentinvites
    )
        and
    to_attending_status_id in
    (
        select id from mainPage_AttendingStatus where status = 'invited'
        and updated > '%s'
    )
    '''

    a_week_ago = datetime.now() - timedelta(7)

    query = raw_query % a_week_ago

    invited_status_dbos = Invited_Status.objects.raw(query)

    for dbo in invited_status_dbos:
       invite(type="invite", invited_status_id = dbo.id) 






