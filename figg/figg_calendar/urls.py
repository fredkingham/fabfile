"""URLs module"""
from django.conf.urls.defaults import patterns
import views
from django.views.generic.simple import direct_to_template
from django.conf import settings

urlpatterns=patterns('',
        (r'^(?i)f/tracking/get_profile/', views.get_profile),
        (r'^(?i)f/tracking/select', views.select),
        (r'^f/tracking/all', views.tracking),
        (r'^f/tracking/remove', views.remove),
        (r'f/trackers', views.get_trackers),
        (r'f/tags', views.get_tags)
    )

if settings.DEBUG:
        urlpatterns += patterns('',
            ('^u/followers/test_profile_pic$', direct_to_template, {"template": "test/profile_pic.html" }),
        )


