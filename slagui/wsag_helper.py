import re
import datetime

from slaclient import wsag_model
from slaclient.wsag_model import AgreementStatus
from slaclient.wsag_model import Violation
#from distutils.tests.setuptools_build_ext import if_dl


VIOLATED = AgreementStatus.StatusEnum.VIOLATED
NON_DETERMINED = AgreementStatus.StatusEnum.NON_DETERMINED
FULFILLED = AgreementStatus.StatusEnum.FULFILLED


def get_violations_bydate(violations):
    """Returns a list of violations per date, from a list of violations

    :param violations list[Violation]:
    :rtype: list
    """
    d = dict()
    for v in violations:
        assert isinstance(v, Violation)
        date = v.datetime.date()
        if not date in d:
            d[date] = []
        d[date].append(v)

    result = [(key, d[key]) for key in sorted(d.keys(), reverse=True)]
    return result


class AgreementAnnotator(object):
    """Annotates an agreement with the following attributes:

    agreement.guaranteestatus
    agreement.statusclass
    agreement.guaranteeterms[*].status
    agreement.guaranteeterms[*].statusclass
    agreement.guaranteeterms[*].nviolations
    agreement.guaranteeterms[*].servicelevelobjetive.bounds

    """
    def __init__(self):
        pass

    @staticmethod
    def _get_statusclass(status):
        if status is None or status == "" or status == NON_DETERMINED:
            return "non-determined"
        return "success" if status == FULFILLED else "error"

    @staticmethod
    def _parse_bounds(servicelevel):
        m = None
        p_list = [".*BETWEEN *[(]?(.*), *([^)]*)[)]?",
                  ".*([EQ]) *([0-9]+)",
                  ".*([NE]) *([0-9]+)",
                  ".*([IN]) *([0-9]+)",
                  ".*([G|L][T|E]) *([0-9]+)"]
        for p in p_list:
            pattern = re.compile(p)
            m = pattern.match(servicelevel)
            if m is not None:
                break
        #print "matched"
        #print m.groups()
        return m.groups()

    def _annotate_guaranteeterm(self, term, violations):
        #
        # Annotate a guarantee term: set bounds and violations
        #
        level = term.servicelevelobjective.customservicelevel
        bounds = AgreementAnnotator._parse_bounds(level)
        term.servicelevelobjective.bounds = bounds

        #
        # set status attribute if not set before
        #
        if not hasattr(term, 'status'):
            term.status = wsag_model.AgreementStatus.StatusEnum.NON_DETERMINED
        #
        # TODO: efficiency
        #
        n = 0
        for violation in violations:
            if violation.metric_name == term.servicelevelobjective.kpiname:
                n += 1
        term.nviolations = n

    def _annotate_guaranteeterm_by_status(
            self, agreement, termstatus, violations):
        #
        # Annotate a guarantee term: it is different from the previous
        # one in that this takes the status into account.
        #
        name = termstatus.name
        status = termstatus.status

        term = agreement.guaranteeterms[name]
        term.status = status
        term.statusclass = AgreementAnnotator._get_statusclass(status)
        self._annotate_guaranteeterm(term, violations)

    def annotate_agreement(self, agreement, status=None, violations=()):

        """Annotate an agreement with certain values needed in the templates

        :param wsag_model.Agreement agreement: agreement to annotate
        :param wsag_model.AgreementStatus status: status of the agreement.
        :param violations: list of agreement's violations
            (wsag_model.Violation[])
        """
        a = agreement

        if status is not None:
            a.guaranteestatus = status.guaranteestatus
            a.statusclass = self._get_statusclass(status.guaranteestatus)
            for termstatus in status.guaranteeterms:
                self._annotate_guaranteeterm_by_status(
                    agreement, termstatus, violations)
        else:
            a.guaranteestatus = NON_DETERMINED
            for termname, term in agreement.guaranteeterms.items():
                self._annotate_guaranteeterm(term, violations)
