from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader
from .models import Template, TemplateVersion
from .conf import TEMPLATE_PREFIX


class DatabaseLoader(Loader):
    """
    A custom template loader to load templates from the database.
    """
    def get_template_sources(self, template_name: str, template_dirs=None):
        if template_name.startswith(TEMPLATE_PREFIX):
            yield Origin(
                name=template_name,
                template_name=template_name,
                loader=self,
            )
        else:
            yield from ()

    def get_contents(self, origin):
        template_name = origin.template_name
        print(template_name)
        try:
            template = Template.objects.get(name=template_name)
            version = TemplateVersion.objects.get(template=template, active=True)
            return version.content
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(template_name)
        except TemplateVersion.DoesNotExist:
            raise TemplateDoesNotExist(template_name)
