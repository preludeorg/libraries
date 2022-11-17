import click
from functools import wraps

from prelude_sdk.models.codes import Colors


def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e, fg=Colors.RED.value)
    return handler


def prompt_overwrite_credentials(func):
    @wraps(func)
    def handler(*args, **kwargs):
        click.confirm(f'Overwrite local account credentials for "{args[0].account.profile}" profile?', abort=True)
        func(*args, **kwargs)
    return handler