import os
from os import path
from django.core.management.base import BaseCommand
from ...models import Template, TemplateVersion
from ... import conf


class Command(BaseCommand):
    help = 'Dump templates to disk'

    def add_arguments(self, parser):
        _cwd = os.getcwd()
        parser.add_argument(
            '-d', '--dir',
            dest='dir', action='store', default=_cwd,
            help=f'directory to dump templates to [default: {_cwd}]')

    def handle(self, **options):
        dump_dir = options.get('dir')
        base_path = path.join(dump_dir, conf.TEMPLATES_DIR_NAME)
        print(f'Workdir: {os.getcwd()}')
        print(f'Dumpdir: {base_path}\n')
        print('Dumping:')

        num_failed = 0
        templates = Template.objects.all()
        for template in templates:
            version = TemplateVersion.objects.active(template.name)
            _path = path.join(base_path, template.name)
            if version:
                os.makedirs(path.dirname(_path), exist_ok=True)
                print(f' - {_path}')
                with open(_path, 'w') as f:
                    f.write(version.content)
            else:
                print(f' - NO ACTIVE VERSION: {_path}')
                num_failed += 1

        print(f'\nDumped: {len(templates)-num_failed}, Failed: {num_failed}')
