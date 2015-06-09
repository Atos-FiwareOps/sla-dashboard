"""Django implementation of the templating needed in XIFI.
"""
import pkgutil
import django.template
from django.conf import settings
import slaclient

#
# Package where to read the template files
#
_package = "slaclient.templates.xifi.django"

#
# Filename of the sla-agreement template
#
_AGREEMENT_FILENAME = "agreement.xml"

#
# Filename of the sla-template template
#
_TEMPLATE_FILENAME = "template.xml"


class Factory(object):

    def __init__(self):
        self.slaagreement_tpl = None
        self.slatemplate_tpl = None

    def _lazy_init(self):
        if not settings.configured:
            settings.configure()

    @staticmethod
    def _read(filename):
        string = pkgutil.get_data(_package, filename)
        return string

    def _get_agreement_tpl(self):
        self._lazy_init()
        if self.slaagreement_tpl is None:
            self.slaagreement_tpl = Factory._read(_AGREEMENT_FILENAME)
        return self.slaagreement_tpl

    def _get_template_tpl(self):
        self._lazy_init()
        if self.slatemplate_tpl is None:
            self.slatemplate_tpl = Factory._read(_TEMPLATE_FILENAME)
        return self.slatemplate_tpl

    def slaagreement(self):
        tpl = self._get_agreement_tpl()
        result = Template(tpl)
        return result

    def slatemplate(self):
        tpl = self._get_template_tpl()
        result = Template(tpl)
        return result


class Template(slaclient.templates.Template):

    def __init__(self, string):
        self.impl = django.template.Template(string)

    def render(self, data):
        context = django.template.Context(dict(data=data))
        result = self.impl.render(context)
        return result
