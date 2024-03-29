import copy
import json
import logging
from collections import namedtuple
from datetime import datetime
from typing import Tuple
from os.path import join
from django.db import transaction, models
from django.core import serializers
from django.core.mail import EmailMessage
from django.template import loader
from django.utils.text import slugify
from .models import Template, TemplateVersion, MailConfig, EmailLog
from . import conf

logger = logging.getLogger(__name__)


Message = namedtuple('Message', [
    'subject',
    'from_email',
    'to_email',
    'body'
])


def _dump(obj) -> str:
    class ObjectEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, models.Model):
                return serializers.serialize('json', [o])
    return json.dumps(obj, cls=ObjectEncoder, indent=4)


@transaction.atomic
def _get_mail_config(
        config_name: str,
        template_content: str = conf.TEMPLATE_CONTENT_DEFAULT,
        default_subject: str = conf.DEFAULT_SUBJECT,
        default_from_email: str = conf.DEFAULT_FROM_EMAIL
) -> Tuple[MailConfig, bool]:
    """
    Loads a MailConfig from DB based on the config_name. If it doesn't exist
    it will be created along with proper Template and TemplateVersion
    instances.

    Args:
        config_name:
        template_content:
        default_subject:
        default_from_email:

    Returns:
        MailConfig: mail config instance
    """
    mail_config = MailConfig.objects.filter(name=config_name).first()
    if mail_config:
        return mail_config, False

    _normalized = slugify(config_name.lower().replace('.', '_'))
    template_name = join(conf.TEMPLATE_PREFIX, f'{_normalized}.html')
    template = Template.objects.create(
        name=template_name
    )
    TemplateVersion.objects.create(
        template=template,
        name='initial',
        active=True,
        content=template_content
    )
    mail_config = MailConfig.objects.create(
        template=template,
        name=config_name,
        description=f'Automatically created on {datetime.now()}',
        subject=default_subject,
        from_email=default_from_email
    )
    return mail_config, True


def render(config_name: str, to_email: str, context: dict) -> Message:
    """
    Loads a MailConfig from DB based on the config_name and creates a Message
    based on the config and template.

    If a MailConfig doesn't exist it will be automatically created and a
    dummy template will be used to render the message.

    Args:
        config_name: name of the MailConfig
        to_email: send to
        context: variables to pass to the template

    Returns:
        Message: mail message which is ready to be send
    """
    mail_config, created = _get_mail_config(config_name)
    subject = mail_config.subject
    from_email = mail_config.from_email

    _context = copy.deepcopy(context) if context else {}
    _context.update({
        'subject': subject,
        'from': from_email,
        'to': to_email,
        'te_base_url': conf.BASE_URL,
        'te_template': mail_config.template.name,
    })

    # Add a dump of the context to the context for debugging purposes
    _context.update(te_context_dump=_dump(_context))
    template = loader.get_template(mail_config.template.name)
    rendered = template.render(_context)
    return Message(
        subject=subject,
        from_email=from_email,
        to_email=to_email,
        body=rendered
    )


def render_version(template_version_name: str, context: dict) -> str:
    _context = copy.deepcopy(context) if context else {}
    _context.update({
        'subject': conf.DEFAULT_SUBJECT,
        'from': conf.DEFAULT_FROM_EMAIL,
        'to': conf.DUMMY_EMAIL,
        'te_base_url': conf.BASE_URL
    })
    _context.update(te_context_dump=_dump(_context))
    template = loader.get_template(template_version_name)
    rendered = template.render(_context)
    return rendered


def send(subject: str, from_email: str, to_email: str, body: str, connection=None) -> int:
    """
    Send a mail and log it.

    Args:
        subject: subject of the mail
        from_email: from email
        to_email: to email
        body: body of the mail
        connection: Django Email backend to use

    Returns:
        int: the pk of the email log
    """
    def _classname(klass):
        return f'{klass.__module__}.{klass.__name__}'

    mailed = False
    class_name = None
    message_id = None
    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            to=[to_email],
            from_email=from_email,
            connection=connection
        )
        message.content_subtype = "html"
        message.send(fail_silently=False)
        mailed = True
        class_name = _classname(message.connection.__class__)

        # If Anymail is used as EmailBackend we'll try to get the message_id
        if hasattr(message, 'anymail_status'):
            message_id = message.anymail_status.message_id
    except Exception:
        logger.exception('Failed to send e-mail message to: %s', to_email)

    msg = EmailLog.objects.create(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        body=body,
        ok=mailed,
        service=class_name,
        message_id=message_id
    )
    return msg.pk


def issue(config_name: str, to_email: str, context: dict, connection=None) -> int:
    """
    Renders and & sends a mail.

    Args:
        config_name:
        to_email:
        context:
        connection:

    Returns:
        int: the pk of the email log
    """
    message = render(config_name, to_email, context)
    return send(message.subject, message.from_email, message.to_email, message.body, connection)


@transaction.atomic
def delete(pk: int):
    TemplateVersion.objects.filter(template__pk=pk).delete()
    Template.objects.get(pk=pk).delete()
