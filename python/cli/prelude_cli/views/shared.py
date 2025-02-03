from functools import wraps
from rich import print_json
from rich.progress import Progress, TextColumn, SpinnerColumn


def pretty_print(func):
    @wraps(func)
    def handler(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            msg = None
            if isinstance(res, tuple):
                res, msg = res
            if not isinstance(res, list):
                res = [res]
            return print_json(data=dict(status="complete", results=res, message=msg))
        except Exception as e:
            return print_json(
                data=dict(
                    status="error",
                    results=None,
                    message=" ".join(str(arg) for arg in e.args),
                )
            )

    return handler


class Spinner(Progress):
    def __init__(self, description="Loading"):
        super().__init__(
            SpinnerColumn(style="green", spinner_name="line"),
            TextColumn("[green]{task.description}..."),
            transient=True,
            refresh_per_second=10,
        )
        self.add_task(description)
