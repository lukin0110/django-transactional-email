"""
RATIONALE

To render or send templated emails other Django apps can only interact with
top-level defined functions, which are exported by __all__.

To avoid import hell when Django is loading it's required to wrap all the
render and send functions and use local imports. Django will fail to load
this app if models are imported in the __init__.py file.
"""
__version__ = '0.3.0'

default_app_config = 'transactional_email.apps.TransactionalEmailConfig'


def render(config_name: str, to_email: str, context: dict):
    """
    Render a template.

    Args:
        config_name: name of the MailConfig
        to_email: send to
        context: variables to pass to the template

    Returns:
        Message: mail message which is ready to be send
    """
    from .utils import render as _render
    return _render(config_name, to_email, context)


def send(subject: str,
         from_email: str,
         to_email: str,
         body: str,
         connection=None) -> int:
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
    from .utils import send as _send
    return _send(subject, from_email, to_email, body, connection)


def issue(config_name: str, to_email: str, context, connection=None) -> int:
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
    from .utils import issue as _issue
    return _issue(config_name, to_email, context, connection)


__all__ = [
    'render',
    'send',
    'issue',
    'urls'
]
