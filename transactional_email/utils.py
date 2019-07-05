import copy
import json
import logging
from collections import namedtuple
from datetime import datetime
from typing import Tuple
from os.path import join
from django.db import transaction
from django.core.mail import EmailMessage
from django.template import loader
from .models import Template, TemplateVersion, MailConfig, EmailLog
from . import conf

logger = logging.getLogger(__name__)


Message = namedtuple('Message', [
    'subject',
    'from_email',
    'to_email',
    'body'
])


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

    template_name = join(conf.TEMPLATE_PREFIX, f'{config_name}.html')
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
    _context = {
        'subject': subject,
        'from': from_email,
        'to': to_email,
    }
    if context:
        _context.update(copy.deepcopy(context))
        # Add a dump of the context to the context for debugging purposes
        _context.update(context_dump=json.dumps(_context, indent=4))

    template = loader.get_template(mail_config.template.name)
    rendered = template.render(_context)

    return Message(
        subject=subject,
        from_email=from_email,
        to_email=to_email,
        body=rendered
    )


def send(subject: str, from_email: str, to_email: str, body: str) -> None:
    mailed = False
    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            to=[to_email],
            from_email=from_email
        )
        message.content_subtype = "html"
        message.send(fail_silently=False)
        mailed = True
    except Exception:
        logger.warning('Failed to send e-mail message to: %s', to_email)

    EmailLog.objects.create(
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        body=body,
        ok=mailed,
        service=None,
        message_id=None
    )


def issue(config_name: str, to_email: str, context) -> None:
    message = render(config_name, to_email, context)
    send(message.subject, message.from_email, message.to_email, message.body)
