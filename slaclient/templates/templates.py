"""This module and submodules offers a generic way to create ws-agreement
representations from structured data, by using templates.

Each submodule (corresponding to a project) is responsible to declare
the structured data to be used as input, and handle the specific template
library.

This module only defines a sample interface to be used for each Template object
used by each project.

Sample usage (read specific submodules' docs):
data = slaclient.<project>.Input(...)
tpl = slaclient.<project>.Template(...)
tpl.render(data)

"""


class Template(object):

    def __init__(self, file_):
        """This is the interface that all project templates should "implement".

        It mimics the behavior of django templates.
        """
        pass

    def render(self, data):
        """Renders this template using 'data' as input.
        """
        pass
