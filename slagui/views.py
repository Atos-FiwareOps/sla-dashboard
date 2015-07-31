# -*- coding: utf-8 -*-

import traceback
import urlparse
import json
import sys
import unicodedata
import re

from slaformat import guiformatter

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.conf import settings
from django.core.urlresolvers import reverse
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
import requests
from requests.auth import HTTPBasicAuth
import oauth2 as oauth
from django.contrib import auth

from slaclient import restclient
from slaclient import wsag_model
from slagui.fm_adapter import FMAdapter
from slagui.marketplace_adapter import MarketplaceAdapter
from slagui.util_helper import UtilHelper
import wsag_helper
from keystone_adapter import KeyStoneAdapter

from django.core.cache import cache
from __builtin__ import str


#
# This is not thread safe and there may be problems if SLA_MANAGER_URL is not
# a fixed value
#
# See:
# http://blog.roseman.org.uk/2010/02/01/middleware-post-processing-django-gotcha
#
factory = restclient.Factory(settings.SLA_MANAGER_URL)

consumer = oauth.Consumer(settings.SECRET_TOKEN, settings.SECRET_KEY)
client = oauth.Client(consumer)

def callbackIdm(request):

	state = request.REQUEST['state']
	code = request.REQUEST['code']
	http = settings.IDM_HTTP_TYPE
	host = settings.IDM_URL
	path = '/oauth2/token'
	params = {
		'grant_type': 'authorization_code',
		'code': code,
		'redirect_uri': settings.IDM_REDIRECT_URL
	}
	try:
		#query = urlparse.urlunparse((http,host,path, '', paramunparse(params), ''))
		query = urlparse.urlunparse((http,host,path, '', '', ''))
		headers = {"auth": HTTPBasicAuth(settings.SECRET_TOKEN, settings.SECRET_KEY)}
		result = requests.post(query, data= params, **headers)
		print result.text
		json_token = json.loads(result.text)

		#userIdm = getUserInformation(json_token)

		user = auth.authenticate(token=json_token)
		auth.login(request, user)
		request.session["user_roles"] = user.roles
		request.session["user_email"] = user.email
		request.session["username"] = user.username

		r_list = []
		for idx, r in enumerate(user.roles):
			r_dict = {
				"id": idx,
				"name": r
			}
			r_list.append(r_dict)
		
		### Collecting the actorId from the keystone of OpenStack using the token of this user
		try:
			keyStoneAdapter = KeyStoneAdapter()
			actorId = keyStoneAdapter.get_actorId(json_token ["access_token"], user.username)
		except Exception, e:
			print ('Error occurred while collecting the ActorId, the system assign the default value for the ActorId')
			print(e)
			actorId = "0000000000000000000000000000000"		
		
		user_org = {
			"name": user.username,
			"roles": r_list,
			"real_org": False,
			"id" : actorId
		}

		request.session["current_organization"] = user_org
		for org in user.organizations:
			org["real_org"] = True
		user.organizations.append(user_org)
		request.session["user_organizations"] = user.organizations
	except Exception, e:
		print("Error details:", sys.exc_info()[0])
		print(e)
		context = {
				'is_error': settings.ERROR_NO_ROLE,
				'err_msg': 'No valid roles exist for this User..',
				'orgs': json.dumps(request.session.get("user_organizations")),
				'current_organization': json.dumps(request.session.get("current_organization")),
			}
		return render(request, 'slagui/agreements.html', context)

	if Rol.CONSUMER in user.roles:
		return HttpResponseRedirect("agreements/")
	elif Rol.PROVIDER in user.roles or Rol.IO in user.roles:
		return HttpResponseRedirect("provider/agreements/")
	else:
		#raise ValueError("rols of the user not supported")
		print "roles of the user are not supported"
		context = {
			'is_error': settings.ERROR_NO_ROLE,
			'err_msg': settings.ERROR_NO_VALID_ROLE,
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(request.session.get("current_organization")),
		}
		return render(request, 'slagui/agreements.html', context)
def idm_login(request):

	http = 'http'
	host = settings.IDM_URL
	path = '/oauth2/authorize'
	params = {
		'response_type': 'code',
		'client_id': settings.IDM_CLIENT_ID,
		'state': settings.IDM_LOGIN_STATE,
		'redirect_uri': settings.IDM_REDIRECT_URL
	}
	query = urlparse.urlunparse((http, host, path, '', guiformatter.paramunparse(params), ''))
	return HttpResponseRedirect(query)


@login_required
def idm_logout(request):
	auth.logout(request)
	return render(request, 'slagui/logout.html', {})


class Rol(object):
	CONSUMER = "Consumer"
	PROVIDER = "ServiceProvider"
	IO = "IO"


class FilterForm(forms.Form):
	_attrs = {'class': 'form-control'}
	exclude = ()
	status = forms.ChoiceField(
		choices=[
			('', 'All'),
			(wsag_model.AgreementStatus.StatusEnum.FULFILLED, 'Fulfilled'),
			(wsag_model.AgreementStatus.StatusEnum.VIOLATED, 'Violated'),
			(wsag_model.AgreementStatus.StatusEnum.NON_DETERMINED,
			 'Non determined')],
		widget=forms.Select(attrs=_attrs),
		required=False
	)
	provider = forms.CharField(
		widget=forms.TextInput(attrs=_attrs),
		required=False
	)
	consumer = forms.CharField(
		widget=forms.TextInput(attrs=_attrs),
		required=False
	)


class AgreementsFilter(object):
	def __init__(self, status=None, provider=None, consumer=None):
		self.status = status
		self.provider = provider
		self.consumer = consumer

	def __repr__(self):
		return "<AgreementsFilter(status={}, provider={}, consumer={})>".format(
			self.status, self.provider, self.consumer
		)

	@staticmethod
	def _check(expectedvalue, actualvalue):
		if expectedvalue is None or expectedvalue == '':
			return True
		else:
			return actualvalue == expectedvalue

	def check(self, agreement):
		"""Check if this agreement satisfy the filter.

		The agreement must be previously annotated
		"""
		guaranteestatus = agreement.guaranteestatus
		provider = agreement.context.provider
		consumer = agreement.context.consumer
		return (
			AgreementsFilter._check(self.status, guaranteestatus) and
			AgreementsFilter._check(self.provider, provider) and
			AgreementsFilter._check(self.consumer, consumer)
		)


class ContactForm(forms.Form):
	subject = forms.CharField(max_length=100)
	message = forms.CharField()
	sender = forms.EmailField()
	cc_myself = forms.BooleanField(required=False)


@login_required
def index_agreements(request):
	if not request.session.get("user_roles"):
		context = {
				'is_error': settings.ERROR_NO_ROLE,
				'err_msg': 'No valid roles exist for this User..'
			}
		return render(request, 'index.html', context)
	if Rol.CONSUMER in request.session.get("user_roles"):
		if request.GET.get("org"):
			return HttpResponseRedirect("agreements?org=" + request.GET.get("org"))
		else:
			return HttpResponseRedirect("agreements")
	elif Rol.PROVIDER in request.session.get("user_roles") or Rol.IO in request.session.get("user_roles"):
		return HttpResponseRedirect("provider/agreements/")
	else:
		#raise ValueError("rols of the user not supported")
		context = {
			'is_error': settings.ERROR_NO_ROLE,
			'err_msg': settings.ERROR_NO_VALID_ROLE,
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(request.session.get("current_organization")),
		}
		return render(request, 'slagui/agreements.html', context)

def retrieve_provider_list():
	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
	r = requests.get(settings.SLA_MANAGER_URL + '/providers', headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	return json.loads(r.content)

@login_required
def agreements_summary(request, is_provider=False):
	"""
	:param django.http.HttpRequest request:
	:param bool is_provider:
	"""
	user = request.user
	consumer_id = None
	provider_id = None
	agreement_id = None
	#
	# Save rol in session
	#
	#request.session["rol"] = rol

	filter_ = None
	form = FilterForm(request.GET)
	if form.is_valid():
		print "IS VALID"
		filter_ = _get_filter_from_form(form)
	if filter_ is None:
		form = FilterForm()
	agreements = []
	show_form = False
	current_roles = []
	try:
		if request.GET.get("org"):
			for organization in request.session.get("user_organizations"):
				if organization["name"] == request.GET.get("org"):
					request.session["current_organization"] = None
					request.session["current_organization"] = organization
					c_org = []
					for r in request.session["current_organization"]["roles"]:
						c_org.append(r["name"])
					if request.session["current_organization"]["real_org"] == False:
						if Rol.CONSUMER in c_org:
							show_form = True
							break
					else:
						for r in c_org:
							if Rol.CONSUMER == r["name"]:
								show_form = True
								break
		else:
			c_org = []
			for r in request.session["current_organization"]["roles"]:
				c_org.append(r["name"])
			if Rol.CONSUMER in c_org:
				show_form = True
			else:
				show_form = False
	except:
		success = ""
	if request.GET.get("org"):
		for organization in request.session.get("user_organizations"):
			if organization["name"] == request.GET.get("org"):
				for ro in organization['roles']:
					current_roles.append(ro['name'])
	else:
		for ro in request.session.get("current_organization")["roles"]:
			if ro:
				current_roles.append(ro["name"])

	if Rol.PROVIDER in current_roles or Rol.IO in current_roles:
		user_id = user.username
		##This change is temporally, we need to be coherent with the provider creation.
		#provider_id = request.session.get("user_email")
		#provider_id = user.username
		provider_id = request.session.get("current_organization")["name"]
		try:
			agreements = _get_agreements(
				agreement_id, provider_id=provider_id, filter_=filter_)
		except:
			traceback.print_exc()
		form.exclude = ('provider',)
	elif Rol.CONSUMER in current_roles:
		show_form = True
		user_id = consumer_id
		#consumer_id = _get_consumer_id()
		consumer_id = request.session.get("user_email")
		agreements = _get_agreements(
			agreement_id, consumer_id=consumer_id, filter_=filter_)
		form.exclude = ('consumer',)
	else:
		#raise ValueError("rol '{}' not supported".format(rol))
		print "rol not supported"
		context = {
			'is_error': settings.ERROR_NO_ROLE,
			'err_msg': settings.ERROR_NO_VALID_ROLE,
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(request.session.get("current_organization")),
		}
		return render(request, 'slagui/agreements.html', context)
	for a in agreements:
		a.t_name = get_template_name(a.context.template_id)
	success = request.GET.get("success")
	message = request.GET.get("message")
	paas = None
	paas_err = None
	try:
		#We need to use the id of the TenantId asociated to the Organization of Cloud
		#paas = get_agreement_paas(request.user.username)
		paas = get_agreement_paas(request.session.get("current_organization")['id'])
	except Exception, e:
		paas_err = str(e)
		print("Error: msg={}".format(str(e)))
	saas = None
	saas_err = None
	try:
		saas = get_agreement_saas(request)
	except Exception, e:
		saas_err = str(e)
		print("Error: msg={}".format(str(e)))
	context = {
		'orgs': json.dumps(request.session.get("user_organizations")),
		'current_organization': json.dumps(request.session.get("current_organization")),
		'user_id': user_id,
		'agreements': agreements,
		'success': success,
		'message': message,
		'form': form,
		'show_form': show_form,
		'paas': paas,
		'saas': saas
	}
	if paas_err:
		context['paas_err'] = paas_err.decode('utf-8', 'ignore')
	if saas_err:
		context['saas_err'] = saas_err.decode('utf-8', 'ignore')
	return render(request, 'slagui/agreements.html', context)

def get_template_name(id):
	t = get_template(id)
	return t["name"]

@login_required
#@require_http_methods("POST")
def create_agreement(request):
	rp = request.POST#request params
	guarantee_terms = []
	s_properties = []
	variables = []
	template = get_template(rp.get('tempid'))
	agreement_name = rp.get('aname')
	if rp.get('grRowNum'):
		for x in range(1, int(rp.get('grRowNum')) + 1):
			sname = guiformatter.machineReadableMetric(rp.get('sname' + str(x)))
			sp = {
				"name": sname,
				"metric": UtilHelper._metric_type.get(sname),
				"location": UtilHelper._metric_location.get(sname)
			}
			variables.append(sp)
		variable_set = {"variables": variables}
		inners_properties = {
			"variableSet": variable_set,
			"name": "ServiceProperties",
			"serviceName": str(template["context"]["service"])
		}
		s_properties.append(inners_properties)
		const = {}
		for y in range(1, int(rp.get('grRowNum')) + 1):
			gname = guiformatter.machineReadableMetric(rp.get("gname" + str(y)))
			const["constraint"] = (gname + " " +
								   rp.get("cons" + str(y)) + " " +
								   rp.get("consval" + str(y)))
			
			policy_obj = rp.get("polval" + str(y))
			if u"Real time" not in policy_obj:
				const["policy"] = "(1 breach, " + guiformatter.getIntervalFromPolicy(policy_obj) + " hours)"
			
			gr = {
				"name": gname,
				"serviceScope": {
					"serviceName": str(template["context"]["service"]),
					"value": str(template["context"]["service"]),
				},
				"serviceLevelObjetive": {
					"kpitarget": {
						"kpiName": gname,
						"customServiceLevel": json.dumps(const)
					}
				}
			}
			guarantee_terms.append(gr)

	doto = {
		"context": {
			"agreementInitiator": request.session.get("user_email"),
			"agreementResponder": str(template["context"]["agreementInitiator"]),
			"serviceProvider": "AgreementResponder",
			"service": str(template["context"]["service"]),
			"expirationTime": str(template["context"]["expirationTime"]),
			"templateId": str(rp.get('tempid'))
		},
		"name": agreement_name,
		"terms": {
		"allTerms": {
			"serviceDescriptionTerm": {
				"name": None,
				"serviceName": None
			},
			"serviceProperties": s_properties,
			"guaranteeTerms": guarantee_terms
		}
	}
	}
	sla_url = settings.SLA_MANAGER_URL + '/agreements'

	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER, 'content-type': settings.JSON_HEADER}
	r = requests.post(sla_url, data=json.dumps(doto), headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	context = ""
	resultinfo = r._content
	data = json.loads(resultinfo)
	if not r.ok:
		message = data.get("message")
		raise Exception(message)
	else:
		agreementId = data.get("elementId")
		try:
			success = request.GET.get("success")
			__start_agreement(request, agreementId)
		except:
			success = ""
		context = {"success": success }

	return render(request, 'slagui/agreements.html', context)

@login_required
def create_template(request):
	rp = request.POST#request params
	guarantee_terms = []
	context = {
		"msg": "success",
		"info": "Template created, please refresh the page.."
	}
	variableinfolist = []
	s_properties = []
	if not rp.get('tsid'):
		raise Exception
	if rp.get('rownum'):
		for x in range(1, int(rp.get('rownum')) + 1):
			service_n = rp.get('sname' + str(x))
			varinfo = {
				"name": service_n,
				"metric": UtilHelper._metric_type.get(service_n),
				"location": UtilHelper._metric_location.get(service_n)
			}
			variableinfolist.append(varinfo)
		variable = {"variable": variableinfolist}
		inners_properties = {
			"serviceName":rp.get('tsid'),
			"variableSet": variable
		}
		s_properties.append(inners_properties)
		const = {}
		for y in range(1, int(rp.get('grrownum')) + 1):
			if(not rp.get("consval" + str(y))):
				context["msg"] = ["error"]
				context["info"] = ["Template creation error! Guarantee values are not correct)"]
				return HttpResponse(json.dumps(context), mimetype="application/json")
			const["constraint"] = rp.get("gname" + str(y)) + " " + rp.get("cons" + str(y)) + " " + rp.get("consval" + str(y))
			
			if int(rp.get("polval" + str(y))) > 0:
				const["policy"] = "(1 breach, " + rp.get("polval" + str(y)) + " hours)"
				
			gr = {
				"name": rp.get('gname' + str(y)),
				"serviceScope": {
					"serviceName": rp.get('tsid'),
					"value": ""
				},
				"serviceLevelObjetive": {
					"kpitarget": {
						"kpiName": rp.get('gname' + str(y)),
						"customServiceLevel": json.dumps(const)
					}
				}
			}
			guarantee_terms.append(gr)
		if not guarantee_terms:
			context["msg"] = ["error"]
			context["info"] = ["Template creation error! There must be at least 1 guarantee term.."]
			return HttpResponse(json.dumps(context), mimetype="application/json")

	doto = {
		"name": str(rp.get('tname')),
		"context": {
			"agreementInitiator": request.session["current_organization"]['name'],
			"agreementResponder": None,
			"serviceProvider": "AgreementInitiator",
			"service": rp.get('tsid'),
			"expirationTime": (rp.get('template_date').replace(' ', 'T') + 'CET').encode('utf8')
		},
		"terms": {
		"allTerms": {
			"serviceDescriptionTerm": {
				"name": None,
				"serviceName": None
			},
			"serviceProperties": s_properties,
			"guaranteeTerms": guarantee_terms
		}
	}
	}
	try:
		#check if provider exist in the database
		#if not then create provider using email address as provider uui
		prov_list = retrieve_provider_list()
		prov_exist = False
		for it in prov_list:
			if it["uuid"] == request.session["current_organization"]['name']:
				prov_exist = True
				break
		if not prov_exist:#provider does not exist, trying to create privder..
			headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER, 'Content-type': settings.JSON_HEADER}
			p = {"uuid": request.session["current_organization"]['name'], "name": request.session["current_organization"]['name']}
			res = requests.post(settings.SLA_MANAGER_URL + '/providers', data=json.dumps(p), headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))

	except:
		context["msg"] = ["error"]
		context["info"] = ["Template creation error! Provider uuid/email error.."]
		return HttpResponse(json.dumps(context), mimetype="application/json")
	try:
		headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER, 'content-type': settings.JSON_HEADER}
		print json.dumps(doto)
		r = requests.post(settings.SLA_MANAGER_URL + '/templates', data=json.dumps(doto), headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
		c = r.status_code
		if not (c == 200 or c == 201 or c == 202 or c == 204):
			raise Exception
	except Exception as ex:
		print ex
		context["msg"] = ["error"]
		context["info"] = ["Template creation error!"]
	return HttpResponse(json.dumps(context), mimetype="application/json")

@login_required
def agreement_update(request):
	agreement_id = request.POST['agrid']
	sla_url = settings.SLA_MANAGER_URL + "/enforcements/" + agreement_id + "/start"
	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
	r = requests.put(sla_url, headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	if "has started" not in r._content:
		print "enforcement start error with agreement id: " + agreement_id
		raise Exception
	return render(request, 'slagui/agreements.html', {})

@login_required
def agreement_details(request, agreement_id):
	annotator = wsag_helper.AgreementAnnotator()
	agreement = _get_agreement(agreement_id)
	violations = _get_agreement_violations(agreement_id)
	status = _get_agreement_status(agreement_id)
	annotator.annotate_agreement(agreement, status, violations)

	violations_by_date = wsag_helper.get_violations_bydate(violations)
	violations_pie_chart = []
	for k, v in agreement.guaranteeterms.items():
		b = {"label": v.servicelevelobjective.kpiname,
			 "value": v.nviolations}
		violations_pie_chart.append(b.copy())
	temp = json.dumps(violations_pie_chart)

	context = {
		'backurl': _get_backurl(request),
		'agreement_id': agreement_id,
		'agreement': agreement,
		'status': status,
		'violations_by_date': violations_by_date,
		'violations_pie_chart': temp
	}
	return render(request, 'slagui/agreement_detail.html', context)


@login_required
def agreement_term_violations(request, agreement_id, guarantee_name):
	annotator = wsag_helper.AgreementAnnotator()
	agreement = _get_agreement(agreement_id)
	violations = _get_agreement_violations(agreement_id, guarantee_name)
	annotator.annotate_agreement(agreement)
	violations_list = violations
	page = request.GET.get('page')
	if not page or page is None:
		page = 1
	paginator = None
	try:
		paginator = Paginator(violations_list, 20)
		violations_list = paginator.page(page)
	except PageNotAnInteger:
		violations_list = paginator.page(1)
	except EmptyPage:
		violations_list = paginator.page(paginator.num_pages)
	context = {
		'backurl': _get_backurl(request),
		'agreement_id': agreement_id,
		'guarantee_term': agreement.guaranteeterms[guarantee_name],
		'guarantee_name': guarantee_name,
		'violations': violations,
		'agreement': agreement,
		'violations_list': violations_list
	}
	return render(request, 'slagui/violations.html', context)



def _get_agreements_client():
	return factory.agreements()


def _get_violations_client():
	return factory.violations()


def _get_backurl(request):
	if Rol.CONSUMER in request.session.get("current_organization")["roles"]:
		backurl = reverse(
			'consumer_agreements_summary',
			kwargs=dict(is_provider=False)
		)
	else:
		backurl = reverse(
			'provider_agreements_summary',
			kwargs=dict(is_provider=True)
		)
	return backurl


def _get_agreement(agreement_id):
	"""

	:rtype : wsag_model.Agreement
	"""
	agreements_client = _get_agreements_client()
	agreement, response = agreements_client.getbyid(agreement_id)
	return agreement


def _get_filter_from_form(form):
	data = form.cleaned_data
	result = AgreementsFilter(
		data["status"], data["provider"], data["consumer"])
	print result
	return result


def _get_agreements(agreement_id, provider_id=None, consumer_id=None,
					filter_=None):
	"""Get agreements

	:rtype : list[wsag_model.Agreement]
	:param str agreement_id:
	:param str provider_id:
	:param str consumer_id:
	:param dict[str,str] filter_:
	"""
	agreements_client = _get_agreements_client()
	if agreement_id is None:
		if consumer_id is not None:
			agreements, response = agreements_client.getbyconsumer(consumer_id)
		elif provider_id is not None:
			agreements, response = agreements_client.getbyprovider(provider_id)
		else:
			raise ValueError(
				"Invalid values: consumer_id and provider_id are None")
	else:
		agreement, response = agreements_client.getbyid(agreement_id)
		agreements = [agreement]

	annotator = wsag_helper.AgreementAnnotator()
	for agreement in agreements:
		id_ = agreement.agreement_id
		status = _get_agreement_status(id_)
		annotator.annotate_agreement(agreement, status)

	if filter_ is not None:
		print "FILTERING ", repr(filter_)
		agreements = filter(filter_.check, agreements)
	else:
		print "NOT FILTERING"
	return agreements


def _get_agreements_by_consumer(consumer_id):
	"""

	:rtype : list[wsag_model.Agreement]
	"""
	agreements_client = _get_agreements_client()
	agreements, response = agreements_client.getbyconsumer(consumer_id)
	return agreements


def _get_agreement_status(agreement_id):
	"""

	:rtype : wsag_model.AgreementStatus
	"""
	agreements_client = _get_agreements_client()
	status, response = agreements_client.getstatus(agreement_id)
	return status


def _get_agreement_violations(agreement_id, term=None):
	"""

	:rtype : list[wsag_model.Violation]
	"""
	violations_client = _get_violations_client()
	violations, response = violations_client.getbyagreement(agreement_id, term)
	return violations



def provider_list(request):
	data = []
	i = 0
	for item in retrieve_provider_list():
		d = {}
		d[item["uuid"]] = item["name"]
		data.append(d)
		i += 1
	return data
	#return HttpResponse(json.dumps(data), content_type="application/json")

def template_list(request):
	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
	r = requests.get(settings.SLA_MANAGER_URL + '/templates', headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	data = {}
	if request.GET.get("s"):
		for i in json.loads(r.content):
			if i['context']['service'] == request.GET.get("s"):
				data[i["name"]] = i["templateId"]
	else:
		for item in json.loads(r.content):
			data[item["name"]] = item["templateId"]
	return HttpResponse(json.dumps(data), content_type="application/json")


def is_show_form(request, show_form, user_type):
	if request.GET.get("org"):
		for organization in request.session.get("user_organizations"):
			if organization["name"] == request.GET.get("org"):
				request.session["current_organization"] = None
				request.session["current_organization"] = organization
				if request.session["current_organization"]["real_org"] == False:
					cur_roles = []
					for r in request.session["current_organization"]["roles"]:
						cur_roles.append(r["name"])
					if user_type in cur_roles:
						show_form = True
						break
				else:
					for r in request.session["current_organization"]["roles"]:
						if user_type == r["name"]:
							show_form = True
							break
	else:
		roles = request.session["current_organization"]["roles"]
		if request.session["current_organization"]["real_org"] == True:
			for r in roles:
				if user_type in r["name"]:
					show_form = True
					break
		else:
			for ro in roles:
				if user_type == ro["name"]:
					show_form = True
	return show_form

def get_agreement_paas(cloudId):
	agreement_paas = 'agreement_paas'+cloudId
	if cache.get(agreement_paas):
		p_list = cache.get(agreement_paas)
		return p_list
	else:
		url = settings.DCA_PAAS_URL + cloudId
		#credentials = '{"auth": {"passwordCredentials": {"username":"marketplace.fiwareops.@gmail.com", "password":"Fiware@2014"}}}'
		#To be reviewed
		credentials = None
		fm = FMAdapter()
		paas_list = fm.do_fm_request(url, credentials, True, fm.DCA)
		p_list = convert_paas_id_to_node(paas_list)
		cache.set(agreement_paas, p_list, 60 * 30)
	return p_list

def convert_paas_id_to_node(paas_list):
	p_list= []
	if paas_list:
		fm = FMAdapter()
		credentials = None
		url = settings.FM_VM_URL
		for p in paas_list:
			if p['status']!='P_DELETED':
				try:
					url2 = url.replace('NODE', p['region']) + str(p['id'])
					hostNameValue = None
					try:
						host_name = fm.do_fm_request(url2, credentials, True, fm.FM)
						if host_name['measures']:
							hostNameValue = host_name['measures'][0]['hostName']['value']
					except Exception, e:
						print("Error when calling the FM")
						hostNameValue =""
					p = {'node': hostNameValue,
						 'region': p['region'],
						 'name': p['name']
						}
					p_list.append(p)	
				except Exception, e:
					print("Error parsing PaaS instances" +e.args)
				
	else:
		return {}
	return p_list


def get_agreement_saas(request):
	actorId = request.session.get("current_organization")['id']
	marketplace_url = settings.MARKETPLACE_REGISTERED_SAAS_URL + actorId
	marketplace_adapter = MarketplaceAdapter()
	saas_list = marketplace_adapter.do_marketplace_request(marketplace_url)
	s_list = []
	#Provisional list of SaaS for the SLA demo
	'''
	s = {
		'id': '1',
		'name': 'Public Kurento instance as SaaS ',
		'description': 'Public Kurento instance as SaaS',
		'node': 'Spain2',
		'uuid': '7b18ea58-3beb-4711-8b92-de5205019afe'
	}
	s_list.append(s)
	'''
	if saas_list and len(saas_list) > 0:
		for s in saas_list:
			s = {
				'id': s['id'],
				'name': s["name"],
				'description': s["description"],
				'node': s["region"],
				'uuid': s["uuid"]
			}
			s_list.append(s)
	return s_list


def get_template_saas(request):
	actorId = request.session.get("current_organization")['id']
	marketplace_url = settings.MARKETPLACE_PUBLISHED_SAAS_URL + actorId
	marketplace_adapter = MarketplaceAdapter()
	saas_list = marketplace_adapter.do_marketplace_request(marketplace_url)
	s_list = []
	#Provisional list of SaaS for the SLA demo
	'''
	s = {
		'id': '1',
		'name': 'Public Kurento instance as SaaS ',
		'description': 'Public Kurento instance as SaaS',
		'node': 'Spain2',
		'uuid': '7b18ea58-3beb-4711-8b92-de5205019afe'
	}
	s_list.append(s)
	s = {
		'id': '2',
		'name': 'Public Repository instance as SaaS',
		'description': 'Public Repository instance as SaaS',
		'node': 'Spain2',
		'uuid': '2c4c1043-58fa-4b95-8f5c-313d7db6312e'
	}
	s_list.append(s)
	'''
	
	if saas_list and len(saas_list) > 0:
		for s in saas_list:
			s = {
				'id': s['id'],
				'name': s["name"],
				'description': s["description"],
				'node': s["region"],
				'uuid': s["uuid"]
			}
			s_list.append(s)
	return s_list

def get_template_paas(request):
	org_name = str(request.session.get("current_organization")['name'])
	template_paas = 'template_paas' + org_name 
	p_list = []
	if cache.get(template_paas):
		p_list = cache.get(template_paas)
	else:
		fm = FMAdapter()
		if org_name in fm.org_node_list:
			node = fm.org_node_list[org_name]
			url = fm.dca_request_url.replace('NODE', node)

			credentials = None
			paas_list = fm.do_fm_request( url, credentials, True, fm.FM)
			if paas_list:
				for paas in paas_list['hosts']:
					if 'None' != str(paas['id']):
						p = {'id': paas['id'], 'node': node}
						p_list.append(p)
			else:
				print('No Paas found..')
		cache.set(template_paas, p_list, 60 * 30)
	return p_list
	#return HttpResponse(json.dumps(p_list), content_type="application/json")

def get_measurements(request):
	service_param = request.GET.get('service');
	kind_service = re.search("^(.+)\|.*$", service_param).group(1)
	service_id = re.search("^.+:(.+)$", service_param).group(1)
	
	org_name = str(request.session.get("current_organization")['name'])
	measurements_cache_id = 'measurements' + service_id 
	measurements = []
	if cache.get(measurements_cache_id):
		measurements = cache.get(measurements_cache_id)
	else:
		fm = FMAdapter()
		node = re.search("^.+\|(.+):.*$", service_param).group(1)
			
		if kind_service == u"host" :
			url = fm.dca_request_url.replace('NODE', node) + "/"+ service_id
		else:
			url = fm.vm_request_url.replace('NODE', node) + service_id
		
		credentials = None
		info = fm.do_fm_request( url, credentials, True, fm.FM)
			
		if 'measures' in info:
			for measure_dict in info['measures']:
				for measure in measure_dict.keys():
					if measure not in ['timestamp', 'hostName']:
						measurements.append((measure, guiformatter.humanReadableMetric(measure, True)))
			orderMeasurementsPerName(measurements)
		else:
			print('No services found for ' + url)
			
		cache.set(measurements_cache_id, measurements, 60 * 30)
	return HttpResponse(json.dumps(measurements), content_type="application/json")

def orderMeasurementsPerName(measurements):
	return measurements.sort(key=lambda name: name[1].lower())

@login_required
def get_templates(request):
	org_name = request.GET.get('org', '')
	if org_name:
		print "asd"
	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
	r = requests.get(settings.SLA_MANAGER_URL + '/templates', headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	sc = r.status_code
	paas = None
	t_paas_err = None
	try:
		paas = get_template_paas(request)
	except Exception, e:
		t_paas_err = str(e)
		print "Error PaaS: " + t_paas_err

	saas = None
	t_saas_err = None
	try:
		saas = get_template_saas(request)
	except Exception, e:
		t_saas_err = str(e)
		print "Error SaaS: " + t_saas_err
		
	if 200 == sc or 201 == sc or 204 == sc:
		data = []
		template_list = json.loads(r.content)

		for item in template_list:
			if request.session["current_organization"]["real_org"] == False:
				a = {
					"temp_id": item["templateId"],
					"temp_name": item["name"],
					"exp_date": item["context"]["expirationTime"],
					"service_id": item["context"]["service"]
				}
				data.append(a)
			else:
				if request.session.get("current_organization")["name"] == item["context"]["agreementInitiator"]:
					a = {
						"temp_id": item["templateId"],
						"temp_name": item["name"],
						"exp_date": item["context"]["expirationTime"],
						"service_id": item["context"]["service"]
					}
					data.append(a)
		show_form = False
		try:
			show_form = is_show_form(request, show_form, Rol.PROVIDER)
			if show_form != True:
				show_form = is_show_form(request, show_form, Rol.IO)
			success = request.GET.get("success")
		except:
			success = ""
		cur_org = request.session.get("current_organization")
		if not cur_org:
			context = {
			'is_error': settings.ERROR_NO_ROLE,
			'err_msg': settings.ERROR_NO_VALID_ROLE,
			'orgs': None,
			'current_organization': None,
			}
			return render(request, 'slagui/agreements.html', context)
		cur_roles = []
		for roles in cur_org['roles']:
			cur_roles.append(roles['name'])
		r = ''
		if Rol.IO in cur_roles:
			r = Rol.IO
		elif Rol.PROVIDER:
			r = Rol.PROVIDER
		else:
			r = Rol.CONSUMER
		context = {
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(cur_org),
			"template_list": data,
			"success": success,
			"show_form": show_form,
			'saas': saas,
			'paas': paas,
			'r': r
		}
	else:
		context = {
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(request.session.get("current_organization")),
			"template_list": [],
			"success": '',
			"show_form": False,
			'saas': saas,
			'paas': paas,
			'r': r
		}
	if t_paas_err:
		context['t_paas_err'] = t_paas_err.decode('utf-8', 'ignore')
	if t_saas_err:
		context['t_saas_err'] = t_saas_err.decode('utf-8', 'ignore')
	return render(request, 'slagui/templates.html', context)

def get_template(template_id):
	try:
		#curl -u user:password -H "Accept: application/json" -X GET localhost:8080/sla-service/templates/%1
		headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
		r = requests.get(settings.SLA_MANAGER_URL + '/templates/' + template_id, headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
		t = json.loads(r.content)
		return t
	except:
		return None

#@login_required
def template_details(request, template_id):
	context = {}
	t = get_template(template_id)
	if t:
		te_list = []
		for index, te in enumerate(t["terms"]["allTerms"]["guaranteeTerms"]):
			
			te_item = {
				"name": t["terms"]["allTerms"]["serviceProperties"][0]["variableSet"]["variables"][index]["name"],
				"kpiName": t["terms"]["allTerms"]["serviceProperties"][0]["variableSet"]["variables"][index]["name"],
				"constraint": json.loads(te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"])["constraint"]
			}
			
			if "policy" in te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"]:
				te_item["policy"] = json.loads(te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"])["policy"]
			else:
				te_item["policy"] = ""
			
			te_list.append(te_item)
		context = {
			"temp_name": t["name"],
			"temp_id": t["templateId"],
			"context": t["context"],
			"backurl": reverse('get_templates'),
			"te_list": te_list,
			'orgs': json.dumps(request.session.get("user_organizations")),
			'current_organization': json.dumps(request.session.get("current_organization")),
		}
	else:
		context = {"style": "visibility:"}
		return render(request, 'slagui/template_detail.html', context)
	return render(request, 'slagui/template_detail.html', context)

#@login_required
def template_constraints(request, template_id):
	t = get_template(template_id)
	te_list = []
	if t:
		try:
			for index, te in enumerate(t["terms"]["allTerms"]["guaranteeTerms"]):
				cns = json.loads(te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"])["constraint"].split(" ")
				cns_name = t["terms"]["allTerms"]["serviceProperties"][0]["variableSet"]["variables"][index]["name"]
				kpiName = te["serviceLevelObjetive"]["kpitarget"]["kpiName"]
				te_item = {
					"t_name": t["name"],
					"t_time": t["context"]["expirationTime"],
					"service": t["context"]["service"],
					"provider": t["context"]["agreementInitiator"],
					"cns": cns[1],
					"cns_val": cns[2],
					"cns_name": guiformatter.humanReadableMetric(cns_name),
					"kpiName": guiformatter.humanReadableMetric(kpiName, True)
					}
				
				if "policy" in te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"]:
					policyValue = json.loads(te["serviceLevelObjetive"]["kpitarget"]["customServiceLevel"])["policy"];
					te_item["policy"] = guiformatter.getIntervalFromPolicy(policyValue)
				else:
					te_item["policy"] = ""
				
				te_list.append(te_item)
			print json.dumps(te_list)
		except:
			return HttpResponse(json.dumps([]), content_type="application/json")
	return HttpResponse(json.dumps(te_list), content_type="application/json")

def __start_agreement(request, agreement_id):
	sla_url = settings.SLA_MANAGER_URL + "/enforcements/" + agreement_id + "/start"
	headers = {settings.ACCEPT_HEADER: settings.JSON_HEADER}
	r = requests.put(sla_url, headers=headers, auth=(settings.SLA_MANAGER_USER, settings.SLA_MANAGER_PASSWORD))
	if "has started" not in r._content:
		print "enforcement start error with agreement id: " + agreement_id
		raise Exception("enforcement start error with agreement id: " + agreement_id)
