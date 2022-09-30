import click
from functools import wraps

from detect_sdk.models.codes import Colors


def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e, fg=Colors.RED.value)
    return handler
