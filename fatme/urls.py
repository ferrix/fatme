from django.conf import settings
from django.conf.urls import url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    url(r'^$', 'fatme.views.home', name='home'),
    url(r'^api/weight/$', 'fatme.views.new_weight', name='new_weight'),
    url(r'^api/weight/latest/$', 'fatme.views.last_json', name='latest'),
    url(r'^api/weight/csv', 'fatme.views.csvhistory', name='csv'),
]

if getattr(settings, 'WITHINGS_ENABLED', False):
    urlpatterns.extend([
        url(r'^api/withings/auth/$', 'fatme.views.withings_auth_start'),
        url(r'^api/withings/auth/callback/$', 'fatme.views.withings_callback',
            name='withings_callback'),
        url(r'^api/withings/$', 'fatme.views.withings', name='withings'),
        url(r'^api/withings/analyse/$', 'fatme.views.withings_analyse',
            name='withings_analyse'),
        url(r'^api/withings/sync/$', 'fatme.views.withings_sync',
            name='withings_sync'),
        url(r'^api/withings/queue/$', 'fatme.views.withings_queue',
            name='withings_queue'),
        url(r'^api/withings/save/$', 'fatme.views.withings_save',
            name='withings_save'),
    ])
