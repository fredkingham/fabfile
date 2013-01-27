"""URLs module"""
from django.conf.urls.defaults import patterns, url
from notifications import views
from django.conf import settings

urlpatterns = patterns('',
        url(r'^!read_notification/$', views.read_notification),
        url(r'^p/?$', views.updates)
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'!show_email/', views.show_email),
    )
