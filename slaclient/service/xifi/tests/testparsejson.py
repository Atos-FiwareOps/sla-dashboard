# -*- coding: utf-8 -*-

from unittest import TestCase
import datetime
import json

from slaclient.service.xifi import jsonparser


class ParseJsonTestCase(TestCase):

	def setUp(self):

		self.from_json = None

		self.expirationtime = datetime.datetime.combine(
			datetime.date.today(),
			datetime.time(0, 0, 0)
		)

		self.template = dict(
			template_id="template-id",
			template_name="template-name",
			provider="provider-id",
			service_id="service-id",
			expiration_time=self.expirationtime.isoformat(),
			service_properties=[
				dict(servicename=None, name="uptime", metric=None,
					 location=None),
				dict(servicename="service-name1", name="uptime", metric=None,
					 location=""),
				dict(servicename="service-name2", name="metric1",
					 metric="xs:string", location=None),
				dict(servicename="service-name2", name="metric2",
					 metric="xs:double", location="//monitoring/metric2")
			]
		)

		self.agreement = dict(
			agreement_id="agreement-id",
			template_id="template-id",
			agreement_name="agreement-name",
			consumer="consumer-id",
			provider="provider-id",
			service_id="service-id",
			expiration_time=self.expirationtime.isoformat(),
			guarantees=[
				dict(name="sin", bounds=(-1, 1))
			]
		)

	def _check_dict(self, d, is_agreement):
		o = self.from_json(json.dumps(d))
		self.assertEquals(d.get("template_id", None), o.template_id)
		if is_agreement:
			self.assertEquals(d.get("agreement_id"), o.agreement_id or None)
			self.assertEquals(d.get("agreement_name"), o.agreement_name)
			self.assertEquals(d.get("consumer"), o.consumer or None)
		else:
			self.assertEquals(d.get("template_name"), o.template_name or None)
		self.assertEquals(d.get("provider"), o.provider)
		self.assertEquals(d.get("service_id"), o.service_id)
		self.assertEquals(d.get("expiration_time"), o.expiration_time_iso)
		if "service_properties" in d:
			for i in range(0, len(d["service_properties"])):
				self.assertEquals(
					d["service_properties"][i].get("servicename"),
					o.service_properties[i].servicename
				)
				self.assertEquals(
					d["service_properties"][i].get("name"),
					o.service_properties[i].name
				)
				self.assertEquals(
					d["service_properties"][i].get("metric"),
					o.service_properties[i].metric
				)
				self.assertEquals(
					d["service_properties"][i].get("location"),
					o.service_properties[i].location
				)
		if "guarantees" in d:
			for i in range(0, len(d["guarantees"])):
				self.assertEquals(
					d["guarantees"][i].get("name"),
					o.guarantee_terms[i].metric_name
				)
				self.assertEquals(
					d["guarantees"][i].get("bounds"),
					o.guarantee_terms[i].bounds
				)

	def test_template_from_json(self):
		self.from_json = jsonparser.templateinput_from_json

		#
		# Add fields one by one, and check
		#
		d = dict()
		for key in self.template:
			if key == "service_properties":
				d[key] = []
				for prop in self.template[key]:
					d[key].append(prop)
					self._check_dict(d, False)
			else:
				d[key] = self.template[key]
				self._check_dict(d, False)

	def test_agreement_from_json(self):
		self.from_json = jsonparser.agreementinput_from_json

		#
		# Add fields one by one, and check
		#
		d = dict()

		for key in self.agreement:
			if key == "guarantees":
				d[key] = []
				for term in self.agreement[key]:
					d[key].append(term)
					self._check_dict(d, True)
			else:
				d[key] = self.agreement[key]
				self._check_dict(d, True)
