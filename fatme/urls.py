from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'fatme.views.home', name='home'),
    url(r'^api/weight/$', 'fatme.views.new_weight', name='new_weight'),
    url(r'^api/weight/latest/$', 'fatme.views.last_json', name='latest'),
    url(r'^api/weight/csv', 'fatme.views.csvhistory', name='csv'),
    # url(r'^fatme/', include('fatme.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
