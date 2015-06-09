from django.conf.urls import patterns, url
from slagui import views

#handler403 = 'views.forbidden'
urlpatterns = patterns('',
    # eg: /$slaroot/
    #url(r'^$', views.index, name='index'),
    #url(r'^(?P<is_provider>provider/)?agreements[/]$',
    #    views.agreements_summary, name='agreements_summary'),
    url(r'^callbackIdm$', views.callbackIdm, name='callbackIdm'),
    url(r'^login/?$', views.idm_login, name='login'),
    url(r'^logout/?$', views.idm_logout, name='logout'),
    
    url(r'^$',
        views.index_agreements, name='index_agreements'),
    url(r'^agreements[/]$',
        views.agreements_summary,
        kwargs={'is_provider': False},
        name='consumer_agreements_summary'),
    url(r'^provider/agreements[/]$',
        views.agreements_summary,
        kwargs={'is_provider': True},
        name='provider_agreements_summary'),
    url(r'^agreements/(?P<agreement_id>[A-Za-z0-9_.:^-]+)$',
        views.agreements_summary, name='agreement'),
    url(r'^agreements/(?P<agreement_id>[A-Za-z0-9_.:^-]+)/guarantees/(?P<guarantee_name>[A-Za-z0-9_.:^-]+)/violations$', 
        views.agreement_term_violations, name='agreement_term_violations'),
    #url(r'^agreements/(?P<agreement_id>\w+)/violations$',
    #    views.agreement_violations, name='agreement_violations'),
    url(r'^agreements/(?P<agreement_id>[A-Za-z0-9_.:^-]+)/detail$', 
        views.agreement_details, name='agreement_details'),
    url(r'^agreements/update[/]$',
        views.agreement_update, name='agreement_update'),
    url(r'^template[/]$',
        views.create_template, name='create_template'),
    url(r'^providerlist[/]$',
        views.provider_list, name='provider_list'),
    url(r'^templatelist[/]$',
        views.template_list, name='template_list'),
    url(r'^templates[/]$',
        views.get_templates, name='get_templates'),
    url(r'^templates/(?P<template_id>[A-Za-z0-9_.:^-]+)/detail$',
        views.template_details, name='template_details'),
    url(r'^agreement[/]$',
        views.create_agreement, name='create_agreement'),
   url(r'^templatecns/(?P<template_id>[A-Za-z0-9_.:^-]+)/detail$',
        views.template_constraints, name='templatecns'),
    #url(r'^consumer/(?P<consumer_id>\w+)$', views.consumer_agreements, name='consumer_agreements'),

    #url(r'^/?$', views.home, name='home'),
    #url(r'^administration/?$', views.admin, name='admin'),
    #url(r'^catalogue/?$', 'views.catalogue', name='catalogue'),
)
