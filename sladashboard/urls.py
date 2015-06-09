from django.conf.urls import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xifi.views.home', name='home'),
    url(r'^%s'%settings.SLA_GUI_URL, include('slagui.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^login/?$', 'django.contrib.auth.views.login', name='login'),
    #url(r'^logout/?$', 'django.contrib.auth.views.logout', name='logout'),
)
