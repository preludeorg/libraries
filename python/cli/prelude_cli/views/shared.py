import click

from functools import wraps
from rich.progress import Progress, TextColumn, SpinnerColumn

def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e.args[0], fg='red')
    return handler


class Spinner(Progress): 
    def __init__(self, description='Loading'): 
        super().__init__(
            SpinnerColumn(style='green', spinner_name='line'),
            TextColumn('[green]{task.description}...'),
            transient=True, 
            refresh_per_second=10
        )
        self.add_task(description)
