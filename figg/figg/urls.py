from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    url(r'', include('main.urls')),
    url(r'', include('twitter.urls')),
    url(r'', include('social_auth.urls')),
    url(r'', include('figg_calendar.urls')),
    url(r'', include('notifications.urls')),

    # Examples:
    # url(r'^$', 'figg.views.home', name='home'),
    # url(r'^figg/', include('figg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^umedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    )

    urlpatterns += staticfiles_urlpatterns()