import os
from django.core.management.base import BaseCommand
from django.template.utils import get_app_template_dirs
from ...models import Template, TemplateVersion
from ... import conf


class Command(BaseCommand):
    help = 'Load app templates into the database'

    def handle(self, **options):
        ext = '.html'
        app_dirs = get_app_template_dirs('templates')
        template_dirs = [d for d in app_dirs if os.path.isdir(d)]

        for _dir in template_dirs:
            for dir_path, sub_dirs, filenames in os.walk(_dir):
                _cleaned = [
                    f for f in filenames
                    if f.endswith(ext) and not f.startswith(".")
                ]
                for f in _cleaned:
                    path = os.path.join(dir_path, f)
                    name = path.split(_dir)[1]
                    if name.startswith('/'):
                        name = name[1:]
                    name = os.path.join(conf.TEMPLATE_PREFIX, name)

                    print('Creating:', name)
                    template, _ = Template.objects.get_or_create(
                        name=name
                    )
                    TemplateVersion.objects.create(
                        template=template,
                        active=True,
                        content=open(path, 'r', encoding='utf-8').read()
                    )
