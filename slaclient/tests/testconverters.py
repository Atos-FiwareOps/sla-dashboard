# -*- coding: utf-8 -*-

from unittest import TestCase
from pprint import pprint
import json

from slaclient import wsag_model
from slaclient import xmlconverter


class ConvertersTestCase(TestCase):

    def setUp(self):
        self.violation = """
            <violation>
                <uuid>ce0e148f-dfac-4492-bb26-ad2e9a6965ec</uuid>
                <contract_uuid>agreement04</contract_uuid>
                <service_scope></service_scope>
                <metric_name>Performance</metric_name>
                <datetime>2014-01-14T11:28:22Z</datetime>
                <actual_value>0.09555700123360344</actual_value>
            </violation>"""

        self.provider = """
            <provider>
                <uuid>1ad9acb9-8dbc-4fe6-9a0b-4244ab6455da</uuid>
                <name>Provider2</name>
            </provider> """

        self.list = """
            <collection href="/providers">
                <items offset="0" total="2">
                    <provider>
                        <uuid>1ad9acb9-8dbc-4fe6-9a0b-4244ab6455da</uuid>
                        <name>Provider1</name>
                    </provider>
                    <provider>
                        <uuid>2ad9acb9-8dbc-4fe6-9a0b-4244ab6455da</uuid>
                        <name>Provider2</name>
                    </provider>
                </items>
            </collection>"""

        self.agreement_status = """
            {
                "AgreementId":"agreement03",
                "guaranteestatus":"VIOLATED",
                "guaranteeterms":
                    [
                        {"name":"GT_ResponseTime","status":"FULFILLED"},
                        {"name":"GT_Performance","status":"VIOLATED"}
                    ]
            }"""

    def test_agreement(self):
        conv = xmlconverter.AgreementConverter()

        out = xmlconverter.convertfile(conv, "slaclient/tests/agreement.xml")
        """:type : Agreement"""

        self.assertEquals("agreement02", out.agreement_id)
        self.assertEquals("RandomClient", out.context.consumer)
        self.assertEquals("provider-prueba", out.context.provider)
        self.assertEquals("template-2007-12-04", out.context.template_id)
        self.assertEquals("ExampleService", out.context.service)

        #pprint(out)

    def test_template(self):
        conv = xmlconverter.AgreementConverter()

        out = xmlconverter.convertfile(conv, "slaclient/tests/template.xml")
        """:type : Template"""

        self.assertEquals("template02", out.template_id)
        self.assertEquals("RandomClient", out.context.consumer)
        self.assertEquals("provider-prueba", out.context.provider)
        self.assertEquals("ExampleService", out.context.service)
        #pprint(out)

    def test_provider(self):
        conv = xmlconverter.ProviderConverter()
        out = xmlconverter.convertstring(conv, self.provider)
        #pprint(out)

    def test_violation(self):
        conv = xmlconverter.ViolationConverter()
        out = xmlconverter.convertstring(conv, self.violation)
        #pprint(out)

    def test_list(self):
        conv = xmlconverter.ListConverter(xmlconverter.ProviderConverter())
        out = xmlconverter.convertstring(conv, self.list)
        #pprint(out)

    def test_agreement_status_decode(self):
        json_obj = json.loads(self.agreement_status)
        out = wsag_model.AgreementStatus.from_dict(json_obj)
        #pprint(out)
