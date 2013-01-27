import logging
from django.template import RequestContext, Context
from django.utils import simplejson    
from twitter import user_calculation, data_extract
from twitter.models import EarlySignUp, EmailPending
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from common import complex_encoder
from common.validation import safe_get
from mainPage.models import ChosenFew
encoder = complex_encoder.Encoder()
logger = logging.getLogger(__name__)
from mainPage.views import main_page
from twitter import email_confirmation
from twitter.decorators import one_of_the_chosen_few
from django.template.loader import get_template
from common import validation
from django.core.mail import EmailMultiAlternatives
from notifications import FROM_EMAIL
from django.conf import settings
from twitter import BIGGER, MINI, NORMAL
from django.core import serializers





def get_img(request):
    if request.method == 'GET':
        username = safe_get(request.GET, "username")
        print "using username %s" % username
        img = user_calculation.get_imgs([username], BIGGER)[username]
        return HttpResponse(encoder.encode(img), mimetype='application/json')

    return HttpResponse()

def get_invitees(request):
    ''' returns a list of all twitter followers as UserDisplay objects'''
    
    if request.user.is_authenticated() and request.method == 'GET':
        user = request.user
        tweet_id = request.GET.get("tweet_id")
        encoder = complex_encoder.Encoder()
        followers = user_calculation.get_all_users()
        return HttpResponse(encoder.encode(followers), mimetype='application/json')

    return HttpResponse()

def sign_up(request):

    return_txt = "Something wrong happened... please refresh the page"
    issue = 1

    if request.method == "POST":
        twitter = request.POST.get("twitter")
        result = user_calculation.sign_up(twitter)
        encoder = complex_encoder.Encoder()
        return HttpResponse(encoder.encode(result), mimetype='application/json')

    return HttpResponse(simplejson.dumps({}), mimetype='application/json')

def search_users(request):
    encoder = complex_encoder.Encoder()

    if request.method == 'GET':
        search_term = safe_get(request.GET, "search_term")
        if search_term:
            result = user_calculation.search_users(search_term)
            return HttpResponse(encoder.encode(result), mimetype='application/json')

    return HttpResponse(encoder.encode(1), mimetype='application/json')

def event_info_process(request):

    if request.method == 'POST':
        data = request.POST.get("data") 
        result = data_extract.extract_text(data)
        event_date = None
        event_time = None

        if result:
            event_date, event_time = result

        return HttpResponse(encoder.encode({"date": event_date, "time": event_time}), mimetype='application/json')

    return HttpResponse()

# if a user has a valid email and nothing in the pending table this means it
# has been validated
# if the user has gone the site without arguements and has a valid email then
# we set context["send"] to True
# if the user has just sent an email then context["send"] = True
# if the user had a pending email and then subsequently changed it, we delete
# the existing hash
# the user can only resend a maximum of 20 emails to an email address
# options passed to the template
# sent: (see above)
# flawed: if the form has been posted with an invalid email
# done: if the user has posted a valid form and can now go through to the main
# site
# too many: if the user has sent too many emails
@one_of_the_chosen_few
def email_request(request, username = None, email_hash = None):
    '''request an email from the user'''

    user = request.user
    pending = EmailPending.objects.filter(pending = user).exists() 
    #if user.email and validation.validate_email(user.email) and not pending:
    if True:
        return HttpResponseRedirect('/')

    if request.method == 'GET':
        # the only way a user can have valid email and not have a pending
        if pending and username and email_hash:
            if username == user.username:
                if EmailPending.objects.filter(pending = user, email_hash = email_hash).exists():
                    EmailPending.objects.filter(pending = user, email_hash = email_hash).delete()
                    return email_done(request, user)
                else:
                    return email_pending(request, user)
        elif pending:
            return email_pending(request, user)

    # if the user has posted the form back then they've either
    # posted it for the first time or they've pressed resend
    # send an email and go to the email_pending page
    elif request.method == 'POST':
        email = request.POST.get("email") 
        if not email:
            email = request.user.email
        if email != user.email:
            user.email = email
            EmailPending.objects.filter(pending = user).delete()

        if email and validation.validate_email(email):
            user.save()
            setup_pending(user, email)
            return email_pending(request, user)

    return email_form(request, user)

def email_form(request, user):
    context = {}

    email = user.email
    if not email:
        context["username"] = user.username
    else:
        context["email"] = email

    if "email" in context and not validation.validate_email(context["email"]):
        context["error"] = True
        context["flawed"] = True
        EmailPending.objects.filter(pending = user).delete()
        user.email = ""
        user.save()

    t = get_template('email_request.html')
    html = t.render(RequestContext(request, context))
    return HttpResponse(html)

def email_done(request, user):
    t = get_template('email_confirmed.html')
    html = t.render(RequestContext(request, {}))
    return HttpResponse(html)

def email_pending(request, user):
    t = get_template('email_sent.html')
    amount = EmailPending(pending = user).amount
    context = {}
    if user.email:
        context["email"] = user.email
    else:
        context["username"] = user.username

    if amount > 20:
        context["too_many"] = True
        context["error"] = True

    html = t.render(RequestContext(request, context))
    return HttpResponse(html)

def debug_view(request):
    return email_form(request, User.objects.get(username = "fredkingham"))

def setup_pending(user, email):
    user_email  = user.email
    email_hash = email_confirmation.get_hash(user)

    if not EmailPending.objects.filter(pending = user, email_hash = email_hash).exists():
        pending = EmailPending(pending = user, email_hash = email_hash)
        pending.save()
    else:
        pending = EmailPending.objects.get(pending = user, email_hash = email_hash)

    send_notification(user, email_hash, pending, email)

def send_notification(user, email_hash, pending = False, email = False):
    if not email:
        email = user.email

    if not pending:
        pending = EmailPending.objects.get(pending = user, email_hash = email_hash)

    name = user.first_name
    username = user.username

    if not name:
        name = username

    pending.amount = pending.amount + 1
    pending.save()

    d = Context({"HOME": settings.HOME, "name": name, "username": username, "email_hash": email_hash})
    plaintext = get_template("email_accept.txt")
    html = get_template("email_accept.html")
    text_content = plaintext.render(d)
    html_content = html.render(d)
    to_emails = [email]
    title = "please can you confirm your email address"
    msg = EmailMultiAlternatives(title, text_content, FROM_EMAIL, to_emails)
    msg.attach_alternative(html_content, "text/html")
    logger.info("sending a confirmation email to %s for %s" % (name, email))
    msg.send()

def show_email(request):
    '''this is a dev method to show the html emails for quick editting'''
    user= User.objects.get(username = "fredkingham")
    email_hash = email_confirmation.get_hash(user)
    username = user.username
    if user.first_name:
        name = user.first_name
    else:
        name = username


    context = {"HOME": settings.HOME, "name": name, "username": username, "email_hash": email_hash}
    t = get_template("email_accept.html")
    html = t.render(RequestContext(request, context))
    return HttpResponse(html)















