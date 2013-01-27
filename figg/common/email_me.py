from django.core.mail import send_mail
EMAIL= "fred@fi.gg"
FROM = "fred@fi.gg"


def send(subject, message, from_address = FROM, to_address = EMAIL):
    send_mail(subject, message, from_address, [to_address], fail_silently=False)
