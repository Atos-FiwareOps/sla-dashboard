"""Builds templates/agreements based on input data (in json format), submitting
to sla manager.

It is intended as backend service for a rest interface.

The json input must work together with the templates to form a valid template
 or agreement for Xifi (be careful!)

This (very simple) service is coupled to the way xifi is interpreting
ws-agreement.


"""
import json

import slaclient.templates.xifi
import slaclient.restclient
import jsonparser
from slaclient import wsag_model
from slaclient import restclient


class ServiceContext(object):
    def __init__(self, restfactory, templatefactory=None):
        """
        :type restfactory: restclient.Factory
        """
        self.restfactory = restfactory
        self.templatefactory = templatefactory


def createprovider(json_data, context):
    """Creates a provider in the SlaManager.
    :type json_data:str
    :type context: ServiceContext

    An example input is:
    {
        "uuid": "f4c993580-03fe-41eb-8a21-a56709f9370f",
        "name": "provider-xifi"
    }
    """
    json_obj = json.loads(json_data)
    p = wsag_model.Provider.from_dict(json_obj)
    provider_client = context.restfactory.providers()
    provider_client.create(p)


def createtemplate(json_data, context):
    """Creates a template in the SlaManager

    An example input is:
    {
        "template_id" : "template-id",
        "template_name" : "template-name",
        "provider" : "provider-1",
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

    :type json_data:str
    :type context: ServiceContext
    """
    data = jsonparser.templateinput_from_json(json_data)
    slatemplate = slaclient.templates.xifi.render_slatemplate(data)
    client = context.restfactory.templates()
    client.create(slatemplate)


def createagreement(json_data, context):
    """Creates an agreement in the SlaManager.

    The template with template_id is retrieved and the properties and some
    context info is copied to the agreement.

    An example input is:
    {
        "template_id" : "template-id",
        "agreement_id" : "agreement-id",
        "expiration_time" : "2014-03-28T13:55:00Z",
        "consumer" : "consumer-a",
        "guarantees" : [
            {
                "name" : "uptime",
                "bounds" : [ "0", "1" ]
            }
        ]
    }
    :type json_data:str
    :type context: ServiceContext
    """
    client_templates = context.restfactory.templates()

    # Builds AgreementInput from json
    data = jsonparser.agreementinput_from_json(json_data)
    # Read template from manager
    slatemplate, request = client_templates.getbyid(data.template_id)
    # Copy (overriding if necessary) from template to AgreementInput
    final_data = data.from_template(slatemplate)

    slaagreement = slaclient.templates.xifi.render_slaagreement(final_data)

    client_agreements = context.restfactory.agreements()
    client_agreements.create(slaagreement)
