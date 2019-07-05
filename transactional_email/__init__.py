"""
RATIONALE

To render or send templated emails other Django apps can only interact with
top-level defined functions, which are exported by __all__.

To avoid import hell when Django is loading it's required to wrap all the
render and send functions and use local imports.
"""
__version__ = "0.1.0"

default_app_config = 'transactional_email.apps.TransactionalEmailConfig'


def render(config_name: str, to_email: str, context: dict):
    from .utils import render as _render
    return _render(config_name, to_email, context)


def send(subject: str, from_email: str, to_email: str, body: str, connection=None):
    from .utils import send as _send
    _send(subject, from_email, to_email, body, connection)


def issue(config_name: str, to_email: str, context, connection=None) -> None:
    from .utils import issue as _issue
    _issue(config_name, to_email, context, connection)


__all__ = [
    'render',
    'send',
    'issue'
]
