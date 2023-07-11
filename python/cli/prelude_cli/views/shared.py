import time
import click
import threading

from rich.progress import Progress, SpinnerColumn, TextColumn
from functools import wraps

def handle_api_error(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.secho(e.args[0], fg='red')
    return handler

class Spinner(): 
    busy = False

    def __init__(self, description='Loading'):
       self.description = description
       self.progress = Progress(
            SpinnerColumn(style='green', spinner_name='line'),
            TextColumn(f'[green]{description}'),
            transient=True
        )

    def spinner_task(self):
        with self.progress:
            task = self.progress.add_task(self.description, track=False)
            while self.busy:
                self.progress.update(task)
                time.sleep(0.02)
        
    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        self.progress.stop()
        if exception is not None:
            return False
