from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from ...utils import issue


class Command(BaseCommand):
    help = 'Send a test mail to the super admins'

    def handle(self, *args, **options):
        super_admins = User.objects.filter(is_superuser=True)

        for user in super_admins:
            email = user.email
            issue('test.mail_config', email, {'foo': 'bar'})
            print('Mailed to:', email)
