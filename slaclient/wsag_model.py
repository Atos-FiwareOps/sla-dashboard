"""Contains the object models that correspond to the SlaManager xml/json types
"""


from datetime import datetime


class Agreement(object):

    class Context(object):
        def __init__(self):
            self.expirationtime = datetime.now()
            self.service = ""
            self.initiator = ""
            self.responder = ""
            self.provider = ""
            self.consumer = ""
            self.template_id = ""

        def __repr__(self):
            s = "<Context(" + \
                "expirationtime={}, provider={}, consumer={}, service={})>"
            return s.format(
                repr(self.expirationtime),
                repr(self.provider),
                repr(self.consumer),
                repr(self.service))

    class Property(object):
        def __init__(self, servicename="", name="", metric="", location=""):
            self.servicename = servicename
            self.name = name
            self.metric = metric
            self.location = location

        def __repr__(self):
            str_ = "<Property(name={}, servicename={}, metric={}, location={})>"
            return str_.format(
                repr(self.name),
                repr(self.servicename),
                repr(self.metric),
                repr(self.location))

    class GuaranteeTerm(object):

        class GuaranteeScope(object):
            def __init__(self):
                self.servicename = ""
                self.scope = ""

            def __repr__(self):
                return "<GuaranteeScope(servicename={}, scope={}>)".format(
                    repr(self.servicename),
                    repr(self.scope)
                )

        class ServiceLevelObjective(object):
            def __init__(self):
                self.kpiname = ""
                self.customservicelevel = ""

            def __repr__(self):
                s = "<ServiceLevelObjective(kpiname={}, customservicelevel={})>"
                return s.format(
                    repr(self.kpiname),
                    repr(self.customservicelevel)
                )

        def __init__(self):
            self.name = ""
            self.scopes = []        # item: GuaranteeScope
            """:type : list[Agreement.GuaranteeTerm.GuaranteeScope]"""
            self.servicelevelobjective = \
                Agreement.GuaranteeTerm.ServiceLevelObjective()

        def __repr__(self):
            s = "<GuaranteeTerm(scopes={}, servicelevelobjective={})>"
            return s.format(
                repr(self.scopes),
                repr(self.servicelevelobjective)
            )

    def __init__(self):
        """Simple bean model for a ws-agreement agreement/template
        """
        self.context = Agreement.Context()
        self.name = ""
        self.agreement_id = ""
        self.descriptionterms = {}
        self.variables = {}         # key: Property.name / value: Property
        """:type : dict[str,Agreement.Property]"""
        self.guaranteeterms = {}    # key: GT.name / value: GT
        """:type : dict[str,Agreement.GuaranteeTerm]"""

    def __repr__(self):
        s = ("<Agreement(agreement_id={}, context={}, descriptionterms={}, " +
             "variables={}, guaranteeterms={}>")
        return s.format(
            repr(self.agreement_id),
            repr(self.context),
            repr(self.descriptionterms),
            repr(self.variables),
            repr(self.guaranteeterms)
        )


class Template(Agreement):

    def __init__(self):
        super(Template, self).__init__()
        self.template_id = ""

    def __repr__(self):
        s = ("<Template(template_id={}, context={}, descriptionterms={}, " +
             "variables={}, guaranteeterms={}>")
        return s.format(
            repr(self.template_id),
            repr(self.context),
            repr(self.descriptionterms),
            repr(self.variables),
            repr(self.guaranteeterms)
        )


class AgreementStatus(object):

    class StatusEnum(object):
        VIOLATED = "VIOLATED"
        FULFILLED = "FULFILLED"
        NON_DETERMINED = "NON_DETERMINED"

    class GuaranteeTermStatus(object):
        def __init__(self):
            self.name = ""
            self.status = ""

        def __repr__(self):
            s = "<GuaranteeTermStatus(name='{}' status='{}')>"
            return s.format(self.name, self.status)

    def __init__(self):
        self.agreement_id = ""
        self.guaranteestatus = ""
        self.guaranteeterms = []

    def __repr__(self):
        return (
            "<AgreementStatus( agreement_id={}, guaranteestatus={}, " +
            "guaranteeterms={})>").format(
                self.agreement_id,
                self.guaranteestatus,
                repr(self.guaranteeterms))

    @staticmethod
    def from_dict(d):
        """Creates an AgreementStatus object from a dict structure (e.g.
        a deserialized json string)

        Usage:
        json_obj = json.loads(json_data)
        out = wsag_model.AgreementStatus.from_dict(json_obj)
        """
        o = AgreementStatus()
        o.agreement_id = d["AgreementId"]
        o.guaranteestatus = d["guaranteestatus"]

        for term in d["guaranteeterms"]:
            t = AgreementStatus.GuaranteeTermStatus()
            t.name = term["name"]
            t.status = term["status"]
            o.guaranteeterms.append(t)
        return o


class Violation(object):
    def __init__(self):
        """Simple bean model for a violation"""
        self.uuid = ""
        self.contract_uuid = ""
        self.service_scope = ""
        self.metric_name = ""
        self.datetime = datetime.now()
        self.actual_value = 0

    def __repr__(self):
        return ("<Violation(uuid={}, agremeent_id={}, service_scope={}, " +
            "metric_name={}, datetime={}, actual_value={})>".format(
                self.uuid,
                self.contract_uuid,
                self.service_scope,
                self.metric_name,
                self.datetime,
                self.actual_value)
        )


class Provider(object):
    def __init__(self, uuid="", name=""):
        """Simple bean model for a provider"""
        self.uuid = uuid
        self.name = name

    def __repr__(self):
        return ("<Provider(uuid={}, name={})>".format(
                self.uuid,
                self.name)
        )

    def to_xml(self):
        xml = "<provider><uuid>{}</uuid><name>{}</name></provider>""".format(
            self.uuid,
            self.name
        )
        return xml

    @staticmethod
    def from_dict(d):
        """Creates a Provider object from a dict structure (e.g.
        a deserialized json string)

        Usage:
        json_obj = json.loads(json_data)
        out = wsag_model.Provider.from_dict(json_obj)
        """
        result = Provider(d["uuid"], d["name"])
        return result

