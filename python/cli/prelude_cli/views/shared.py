import click
from functools import wraps

from prelude_sdk.models.codes import Colors


def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e.args[0], fg=Colors.RED.value)
    return handler
