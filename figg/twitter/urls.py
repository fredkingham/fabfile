"""URLs module"""

from django.conf.urls.defaults import patterns, url
from twitter import views
from django.conf import settings

urlpatterns = patterns('',
        url(r'^d/email_request(?:/(?P<username>\w*)/(?P<email_hash>\w*))/$', views.email_request),
        url(r'^d/email_request/$', views.email_request),
        url(r'^d/get_img', views.get_img),
        url(r'd/debug/', views.debug_view),
        (r'^(?i)!event_info_process$', views.event_info_process),
        (r'^(?i)!search_users/$', views.search_users),
        (r'^!get_invitees$', views.get_invitees),
        (r'^!sign_up$', views.sign_up),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'd/show_email/', views.show_email),
    )

