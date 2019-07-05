"""
Constants & configuration variables
"""
from django.conf import settings

# Prefix to add to all templates names.
# The prefix is required to create a separate namespace for the transactional
# e-mail templates. We need to avoid that Django's template system loads
# templates from disk.
TEMPLATE_PREFIX = 'transactional_email/'

# Django template used to send a test e-mail
# Will also be used when a MailConfig is auto-created
TEMPLATE_CONTENT_DEFAULT = '<h1>Default mail</h1>' \
          '<br>From: {{ from }}' \
          '<br>To: {{ to }}' \
          '<br><br>Context dump: <pre>{{ context_dump }}</pre>'

# Defaults for the subject and from e-mail
DEFAULT_SUBJECT = 'Auto generated subject'

# https://docs.djangoproject.com/en/2.2/ref/settings/#default-from-email
DEFAULT_FROM_EMAIL = getattr(
    settings,
    'DEFAULT_FROM_EMAIL',
    'Test Jeffrey <jeffrey@dudeism.com>'
)
