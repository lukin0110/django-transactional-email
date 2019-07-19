import os
from django.core.management.base import BaseCommand
from django.template.utils import get_app_template_dirs
from django.utils.timezone import now
from ...models import Template, TemplateVersion
from ... import conf


class Command(BaseCommand):
    help = 'Load templates into the database from Django apps or a ' \
           'specific directory'

    def add_arguments(self, parser):
        _cwd = os.getcwd()
        parser.add_argument(
            '-d', '--dir',
            dest='dir', action='store', default=None,
            help=f'directory to look for templates')
        parser.add_argument(
            '-a', '--apps',
            dest='apps', action='store_true', default=False,
            help='overwrite existing database templates')

    def handle(self, **options):
        ext = '.html'
        dump_dir = options.get('dir')
        apps = options.get('apps')

        # Decide from where to load templates
        if dump_dir:
            base_path = os.path.join(
                dump_dir, conf.TEMPLATES_DIR_NAME, conf.TEMPLATE_PREFIX)
            print(f'Load templates from: {base_path}\n')
            template_dirs = [base_path]
        elif apps:
            print(f'Load templates from Django Apps\n')
            app_dirs = get_app_template_dirs('templates')
            template_dirs = [d for d in app_dirs if os.path.isdir(d)]
        else:
            print('Must choose an option: --dir or --apps')
            return

        print('Loading:')
        num_created = 0

        for _dir in template_dirs:
            answer = input(f'Load {_dir}? [y/N] ')
            if answer and 'y' == answer.lower():
                num = load_dir(_dir, ext)
                num_created += num

        print(f'\nLoaded: {num_created}')


def load_dir(dirname: str, ext: str) -> int:
    num_created = 0
    for dir_path, sub_dirs, filenames in os.walk(dirname):
        _cleaned = [
            f for f in filenames
            if f.endswith(ext) and not f.startswith(".")
        ]
        for f in _cleaned:
            num_created += 1
            _path = os.path.join(dir_path, f)
            name = _path.split(dirname)[1]
            if name.startswith('/'):
                name = name[1:]
            name = os.path.join(conf.TEMPLATE_PREFIX, name)
            print(f' - {name}')
            version_name = f'imported-' \
                f'{now().strftime("%Y-%m-%d-%H:%M:%S:%f")}'
            template, _ = Template.objects.get_or_create(
                name=name
            )
            TemplateVersion.objects.create(
                template=template,
                name=version_name,
                active=False,
                content=open(_path, 'r', encoding='utf-8').read()
            )
    return num_created
