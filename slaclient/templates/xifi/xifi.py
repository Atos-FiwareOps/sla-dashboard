"""Template system for xifi project.

The specific template system is configured with the factory module variable.

By default, it is set to use django.

Each implementation must define a factory module/object, defining:
* slaagreement()
* slatemplate()

that returns a slaclient.templates.Template-compliant object that performs
the actual render.

This module defines two facade methods:
* render_slaagreement(data)
* render_slatemplate(data)

and the corresponding input classes:
* AgreementInput
* TemplateInput

Usage:
	# Thread safe
	import slaclient.templates.xifi
	data = slaclient.templates.xifi.TemplateInput(template_id="template-test")
	t = slaclient.templates.xifi.django.Factory().slatemplate()
	slatemplate_xml = t.render(data)

	# Non thread safe
	import slaclient.templates.xifi
	data = slaclient.templates.xifi.TemplateInput(template_id="template-test")
	slatemplate_xml = slaclient.templates.xifi.render_slatemplate(data)

Notes about agreements in XiFi:
	The ws-agreement specification does not address where to place the name/id
	of the service (as known outside SLA) being defined in the
	agreement/template xml. So, it has been defined an element
	wsag:Context/sla:Service, whose text is the name/id of the service. This
	is known here as serviceId.

	An agreement/template can represent zero or more than one existing services.
	The guarantee terms, service description terms, etc, use the attribute
	serviceName to reference (internally in the xml) the service. So, there
	could be more than one serviceName in a xml (as opposed to the former
	serviceId). In Xifi, there is only one service per agreement, so we
	can give serviceId and serviceName the same value.

	A ServiceReference defines how a serviceName is known externally: a
	service reference can be a name, a location, a structure containing both...

	The service properties are a set of variables that are used in the guarantee
	terms contraints. So, for example, if a constraint is : "uptime < 90", we
	can have 2 service properties: ActualUptime and DesiredUptime. And the
	constraint will be "ActualUptime < DesiredUptime". This is the theory. But
	we're not going to use the service properties this way. We will not use the
	thresholds as service properties; only the actual metric. So, in this case,
	the service property is defined in ws-agreement as:

		<wsag:Variable Name="Uptime" Metric="xs:double">
			<wsag:Location>service-ping/Uptime</wsag:Location>
		</wsag:Variable>

	The "location" is the strange value here. Ws-agreement says that it is a
	"structural reference" to the place where to find the actual value of the
	metric. The examples I've found are references to the
	ServiceDescriptionTerms in the agreement itself. We are not using SDTs
	(they are used to describe the service to be instantiated), so we can
	extrapolate the location as the "abstract location of the metric".

	In summary, in XiFi, the service properties will hold the metrics being
	monitored for a service.

	And the guarantee terms hold the constraints that are being enforced for
	the service in this agreement (maybe we are only interested in enforcing
	one of the metrics).

	A guarantee term is defined as:
		<wsag:GuaranteeTerm Name="GT_ResponseTime">
			<wsag:ServiceScope ServiceName="service-ping"/>
			<wsag:ServiceLevelObjective>
				<wsag:KPITarget>
					<wsag:KPIName>Uptime</wsag:KPIName>
					<wsag:CustomServiceLevel>
						{"constraint" : "Uptime BETWEEN (90, 100)"}
					</wsag:CustomServiceLevel>
				</wsag:KPITarget>
			</wsag:ServiceLevelObjective>
		</wsag:GuaranteeTerm>

	* Name is a name for the guarantee term. In Xifi, the name will have the
	  value "GT_<metric_name>"
	* ServiceName is an internal reference in the agreement to the service
	  being enforced, as an agreement can created for more than one service.
	  In Xifi, to my knowledge, one service: one agreement, so this service
	  name is not really important.
	* KpiName is a name given to the constraint, and I am using the same name
	  as the service property used in the constraint. This makes more sense
	  when using thresholds as service properties (e.g., a kpi called
	  "uptime" could be defined as :
	  "actual_uptime BETWEEN(lower_uptime, upper_uptime)").

	The CustomServiceLevel is not specified by ws-agreement, so it's something
	  to be defined by the implementation.

"""

from slaclient import wsag_model


from slaclient.templates.xifi.django.factory import Factory
factory = Factory()


def _getfactory():
	#
	# Hardwired above to avoid multheading issues. This will need some
	# refactoring if the factory really needs to be configurable.
	#

	global factory
	#if factory is None:
	#	from slaclient.templates.xifi.django.factory import Factory
	#	factory = Factory()
	return factory


def render_slaagreement(data):
	"""Generate a sla agreement based on the supplied data.

	:type data: AgreementInput
	"""
	template = _getfactory().slaagreement()
	return template.render(data)


def render_slatemplate(data):
	"""Generate a sla template based on the supplied data.

	:type data: TemplateInput
	"""
	template = _getfactory().slatemplate()
	return template.render(data)


class TemplateInput(object):

	def __init__(self,
				template_id="",
				template_name="",
				provider="",
				service_id="",
				expiration_time=None,
				service_properties=()):
		"""Input data to the template for generating a sla-template.

		:param str template_id: optional TemplateId. If not specified, the
		  SlaManager should provide one.
		:param str template_name: optional name for the template.
		:param str service_id: Domain id/name of the service.
		:param str provider: optional Resource Id of the provider party in the
		  agreement. The provider must exist previously in the SlaManager.
		:param expiration_time: optional expiration time of this template.
		:type expiration_time: datetime.datetime
		:param service_properties: Metrics that the provider is able to
		  monitor for this service.
		:type service_properties: list[slaclient.wsag_model.Agreement.Property]
		"""
		self.template_id = template_id
		self.template_name = template_name
		self.service_id = service_id
		self.provider = provider
		self.expiration_time = expiration_time
		self.expiration_time_iso = \
			expiration_time.isoformat() if expiration_time else None
		self.service_properties = service_properties

	def __repr__(self):
		s = "<TemplateInput(template_id={}, template_name={})" \
			"service_id={}, provider={}, expiration_time={}, " \
			"service_properties={}>"
		return s.format(
			self.template_id,
			self.template_name,
			self.service_id,
			self.provider,
			self.expiration_time_iso,
			repr(self.service_properties)
		)


class AgreementInput(object):

	class GuaranteeTerm(object):

		def __init__(self,
					metric_name="",
					bounds=(0, 0)):
			"""Creates a GuaranteeTerm.

			Take into account that the GT's name is based on the metric_name.
			:param str metric_name: name of the service property being enforced.
			:param bounds: (lower, upper) bounds of the metric values.
			:type bounds: (float, float)
			"""
			self.name = "GT_{}".format(metric_name)
			self.metric_name = metric_name
			self.kpiname = metric_name
			self.bounds = bounds

	def __init__(self,
				agreement_id="",
				agreement_name="",
				service_id="",
				consumer="",
				provider="",
				template_id="",
				expiration_time=None,
				service_properties=(),
				guarantee_terms=()):
		"""Input data to the template for generating a sla-agreement

		:param str agreement_id: optional agreement id. If not supplied,
			the SlaManager should create one.
		:param str agreement_name: optional agreement name
		:param str service_id: Domain id/name of the service.
		:param str consumer: Id of the consumer party in the agreement.
		:param str provider: Resource Id of the provider party in the agreement.
		  The provider must exist previously in the SlaManager.
		:param str template_id: TemplateId of the template this agreement is
		  based on.
		:param expiration_time: Expiration time of this agreement.
		:type expiration_time: datetime.datetime
		:param service_properties: Should be the same of the template.
		:type service_properties: list[slaclient.wsag_model.Agreement.Property]
		:param guarantee_terms: Guarantee terms to be enforced in this
		  agreement.
		:type guarantee_terms: list(AgreementInput.GuaranteeTerm)
		"""
		self.agreement_id = agreement_id
		self.agreement_name = agreement_name
		self.service_id = service_id
		self.consumer = consumer
		self.provider = provider
		self.template_id = template_id
		self.expiration_time = expiration_time
		self.expiration_time_iso = \
			expiration_time.isoformat() if expiration_time else None
		self.service_properties = service_properties
		self.guarantee_terms = guarantee_terms

	def __repr__(self):
		s = "<AgreementInput(agreement_id={}, agreement_name={}, " \
			"service_id={}, consumer={}, provider={}, template_id={}, " \
			"expiration_time={}, service_properties={}, guarantee_terms={}>"
		return s.format(
			self.agreement_id,
			self.agreement_name,
			self.service_id,
			self.consumer,
			self.provider,
			self.template_id,
			self.expiration_time,
			repr(self.service_properties),
			repr(self.guarantee_terms)
		)

	def from_template(self, slatemplate):
		"""Return a new agreement based on this agreement and copying info
		(overriding if necessary) from a slatemplate.

		:type slatemplate: wsag_model.Template
		:rtype: AgreementInput
		"""
		#
		# NOTE: templateinput does not address guaranteeterms (yet)
		#
		result = AgreementInput(
			agreement_id=self.agreement_id,
			agreement_name=self.agreement_name,
			service_id=slatemplate.context.service,
			consumer=self.consumer,
			provider=slatemplate.context.provider or self.provider,
			template_id=slatemplate.template_id,
			expiration_time=self.expiration_time,
			service_properties=slatemplate.variables.values(),
			guarantee_terms=self.guarantee_terms
		)
		return result
