class LabelChange:
    add = 'add'
    remove = 'remove'

class AttendingStatus:
    creator = "creator"
    added = "added"
    invited = "invited"
    publicly_added = "openly added"
    privately_added = "privately added"
    mostly_privately_added = "mostly privately added"
    hidden_added = "hidden"
    accepted = "accepted"
    invite = "invite"
    cancelled = "cancelled"
    cancelled_invite = "cancelled_invite"
    attending_statuses = [accepted, added]
    pending = "pending"
    unable = "unable"

class EventOption:
    add = "add"
    accept = "send acceptance"
    unable = "not going"
    stop_attending = "remove"
    invite = "add note"
    cancel = "cancel invitation"
    spam = "mark as spam"

class AttendingOption:
    publically_add = "openly add (just putting it out there)"
    privately_add = "privately add (appear as busy on your public calendar)"
    partial_add = "mostly privately add (but let other people attending see I'm attending)"
    hidden_add = "hidden add, stealth mode, doesn't appear on public calendars at all"   
