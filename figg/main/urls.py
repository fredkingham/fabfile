from django.conf.urls.defaults import patterns, include
from django.views.generic.simple import direct_to_template
from django.contrib.auth.views import login
from mainPage import views


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404=views.page_not_found_404
handler500=views.page_not_found_500






urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'twigg.views.home', name='home'),
    # url(r'^twigg/', include('twigg.foo.urls')),
(r'^!v/(?P<venue>[^/]*)/', views.venue),
('^about$', direct_to_template, {"template": "about.html"}, "about"),
(r'^!invite$', views.invite),
(r'^!admin/', include(admin.site.urls)),
(r'^e/create/$', views.create),
(r'^!event_creator_from_json/$', views.event_creator_from_json),
(r'^!event_creator_from_html/$', views.event_creator_from_html),
(r'^!cv/$', views.create_venue),
(r'^!cov/$', views.commit_venue),
(r'^!get_dateline/$', views.get_dateline),
(r'^!event_option/$', views.event_option),
(r'^!get_notes/$', views.get_notes),
(r'^!img_preview$', views.img_preview),
(r'^!get_all_events$', views.get_all_events),
(r'^!cancel_event/$', views.cancel_event),
(r'^detail_creator/$', views.detail_creator),
(r'^!discuss_creator/$', views.discuss_creator),
(r'^share_note/$', views.share_note),
(r'^share_detail/$', views.share_detail),
(r'!are_users', views.are_users),
(r'!get_attending', views.get_attending),
(r'!get_venues', views.get_venues),
(r'^!search_term/$', views.search_term),
(r's/\w+$', views.search),
(r'submit_venue', views.submit_venue),
(r'get_users', views.get_users),
(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
(r'^!logout?$', views.logout_user),
(r'^i/(?P<series_id>\w+)/trackers/?$', views.series_page),
(r'^i/(?P<series_id>\w+)(?:/d/(?P<for_date>\d\d\d\d/\d\d/\d\d))?/?$', views.series_page),
(r'^i/(?P<tag_name>\w+)/trackers/?$', views.tag_page),
(r'^t/(?P<tag_name>\w+)(?:/d/(?P<for_date>\d\d\d\d/\d\d/\d\d))?/?$', views.tag_page),
(r'^!event_editor/$', views.event_editor),
(r'^(?P<username>\w\w+)/tracking/?$', views.person_page),
(r'^(?P<username>\w\w+)/trackers/?$', views.person_page),
(r'^(?P<username>\w\w+)/tags/?$', views.person_page),
(r'^(?P<username>\w\w+)(?:/d/(?P<for_date>\d\d\d\d/\d\d/\d\d))?/?$', views.person_page),
(r'^accounts/login/$', login),
(r'^accounts/profile/$', views.profile),
(r'^!preview_creator/$', views.preview_creator),
('^l/starter$', direct_to_template, {"template": "starter.html"}),
(r'^$', views.main_page),
(r'^d/(?P<for_date>\d\d\d\d/\d\d/\d\d)/?$', views.main_page),

    # Uncomment the admin/doc line below to enable admin documentation:
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
)





