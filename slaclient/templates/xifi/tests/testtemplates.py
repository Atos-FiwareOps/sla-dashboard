# -*- coding: utf-8 -*-

from unittest import TestCase
import datetime

from slaclient import wsag_model
from slaclient import xmlconverter
import slaclient.templates.xifi
from slaclient.templates.xifi import TemplateInput
from slaclient.templates.xifi import AgreementInput


class TemplatesTestCase(TestCase):

    def setUp(self):
        self.converter = xmlconverter.AgreementConverter()

        self.expirationtime = datetime.datetime.combine(
            datetime.date.today(),
            datetime.time(0, 0, 0)
        )
        self.templateinput = TemplateInput(
            template_id="template-id",
            template_name="template-name",
            service_id="service-name",
            expiration_time=self.expirationtime,
            service_properties=[
                wsag_model.Agreement.Property(
                    name="uptime",
                    metric="xs:double",
                    location="uptime"),
                wsag_model.Agreement.Property(
                    name="responsetime",
                    location="responsetime"),
                wsag_model.Agreement.Property(
                    name="quality",
                    metric="xs:string"),
            ]
        )
        self.agreementinput = AgreementInput(
            agreement_id="agreement-id",
            agreement_name="agreement-name",
            consumer="consumer-id",
            provider="provider-id",
            service_id="service-name",
            template_id="template-id",
            expiration_time=self.expirationtime,
            service_properties=self.templateinput.service_properties,
            guarantee_terms=[
                AgreementInput.GuaranteeTerm(
                    "uptime", (0.9, 1)
                ),
                AgreementInput.GuaranteeTerm(
                    "responsetime", (0, 200)
                )
            ]
        )

    def test_template(self):
        slatemplate = slaclient.templates.xifi.render_slatemplate(
            self.templateinput
        )
        # convert xml to wsag_model classes
        actual = xmlconverter.convertstring(self.converter, slatemplate)
        """:type: wsag_model.Template"""

        expected = self.templateinput

        self.assertEquals(
            expected.template_id,
            actual.template_id
        )
        self._check_common(expected, actual)
        print slatemplate

    def test_agreement(self):
        slaagreement = slaclient.templates.xifi.render_slaagreement(
            self.agreementinput
        )
        # convert xml to wsag_model classes
        actual = xmlconverter.convertstring(self.converter, slaagreement)
        """:type: wsag_model.Agreement"""

        expected = self.agreementinput

        self.assertEquals(
            expected.agreement_id,
            actual.agreement_id
        )
        expected.consumer and self.assertEquals(
            expected.consumer,
            actual.context.consumer
        )
        self._check_common(expected, actual)
        self._check_guarantee_terms(expected, actual)
        print slaagreement

    def _check_common(self, expected, actual):
        if expected.provider:
            self.assertEquals(
                expected.provider,
                actual.context.provider
            )
        self.assertEquals(
            expected.expiration_time_iso,
            actual.context.expirationtime
        )
        self.assertEquals(
            expected.service_id,
            actual.context.service
        )
        self._check_properties(expected, actual)

    def _check_properties(self, expected, actual):
        for expected_prop in expected.service_properties:
            actual_prop = actual.variables[expected_prop.name]
            self.assertEquals(
                expected_prop.name,
                actual_prop.name
            )
            self.assertEquals(
                expected_prop.location or expected_prop.name,
                actual_prop.location
            )
            self.assertEquals(
                expected_prop.metric or 'xs:double',
                actual_prop.metric
            )

    def _check_guarantee_terms(self, expected, actual):
        """
        :type expected: AgreementInput
        :type actual: wsag_model.Agreement
        """
        for expected_term in expected.guarantee_terms:
            actual_term = actual.guaranteeterms[expected_term.name]

            if actual_term is None:
                self.assertEquals(expected_term.name, None)
            self.assertEquals(
                expected_term.kpiname,
                actual_term.servicelevelobjective.kpiname
            )
