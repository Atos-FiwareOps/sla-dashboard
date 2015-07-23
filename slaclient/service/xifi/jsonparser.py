"""

"""

import json
import dateutil.parser

from slaclient import wsag_model
from slaclient.templates.xifi import AgreementInput
from slaclient.templates.xifi import TemplateInput


def templateinput_from_json(json_data):
	"""Creates a TemplateInput from json data.

	:rtype: TemplateInput

	An example input is:
	{
		"agreement_id" : "agreement-id"
		"agreement_name" : "agreement-name",
		"template_id" : "template-id",
		"provider" : "provider",
		"service_id" : "service-id",
		"expiration_time" : "2014-03-28T13:55:00Z",
		"service_properties" : [
			{
				"name" : "uptime",
				"servicename" : "service-a",
				"metric" : "xs:double",
				"location" : "//service-a/uptime"
			}
		]
	}
	"""
	d = json.loads(json_data)
	if "expiration_time" in d:
		d["expiration_time"] = dateutil.parser.parse(d["expiration_time"])

	t = TemplateInput(
		template_id=d.get("template_id", None),
		template_name=d.get("template_name", None),
		provider=d.get("provider", None),
		service_id=d.get("service_id"),
		expiration_time=d.get("expiration_time", None),
		service_properties=_json_parse_service_properties(d)
	)
	return t


def agreementinput_from_json(json_data):
	"""Creates an AgreementInput from json data.

	:rtype: AgreementInput

	An example input is:
	{
		"agreement_id" : "agreement-id"
		"agreement_name" : "agreement-name",
		"template_id" : "template-id",
		"consumer" : "consumer",
		"provider" : "provider",
		"service_id" : "service-id",
		"expiration_time" : "2014-03-28T13:55:00Z",
		"guarantees": [
			{
				"name" : "uptime",
				"bounds" : [ "0", "1" ]
			}
		]
	}
	"""
	d = json.loads(json_data)
	if "expiration_time" in d:
		d["expiration_time"] = dateutil.parser.parse(d["expiration_time"])

	t = AgreementInput(
		agreement_id=d.get("agreement_id", None),
		agreement_name=d.get("agreement_name", None),
		template_id=d.get("template_id", None),
		consumer=d.get("consumer", None),
		provider=d.get("provider", None),
		service_id=d.get("service_id"),
		expiration_time=d.get("expiration_time", None),
		service_properties=_json_parse_service_properties(d),
		guarantee_terms=_json_parse_guarantee_terms(d)
	)
	return t


def _json_parse_service_properties(d):
	"""Parse service properties in a json and translates to Property.
	:type d: dict(str, str)
	:rtype: list(wsag_model.Agreement.Property)
	"""
	result = []
	for sp in d.get("service_properties", None) or ():
		result.append(
			wsag_model.Agreement.Property(
				servicename=sp.get("servicename", None),
				name=sp.get("name", None),
				metric=sp.get("metric", None),
				location=sp.get("location", None)
			)
		)
	return result


def _json_parse_guarantee_terms(d):
	"""Parse guarantee terms in a son and translates to GuaranteeTerm.
	:type d: dict(str, str)
	:rtype: list(wsag_model.AgreementInput.GuaranteeTerm)
	"""
	result = []
	for term in d.get("guarantees", None) or ():
		result.append(
			AgreementInput.GuaranteeTerm(
				metric_name=term["name"],
				bounds=tuple(term["bounds"])
			)
		)
	return result