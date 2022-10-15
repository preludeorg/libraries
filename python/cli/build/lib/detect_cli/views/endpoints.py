import click
from rich import print_json

from detect_sdk.controllers.endpoints_controller import EndpointsController
from detect_sdk.models.codes import Colors
from detect_cli.views.shared import handle_api_error


@click.group()
@click.pass_context
def endpoints(ctx):
    """Interact with endpoints"""
    ctx.obj = EndpointsController(account=ctx.obj)


@endpoints.command('register-endpoint')
@click.option('--tag', help='add a custom tag to this endpoint')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tag):
    """Register a new endpoint"""
    endpoint_token = controller.register_endpoint(name=name, tag=tag)
    click.secho('Endpoint token: %s' % endpoint_token, fg=Colors.GREEN.value)


@endpoints.command('describe-activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.argument('endpoint_id')
@click.pass_obj
@handle_api_error
def describe_activity(controller, endpoint_id, days):
    """ Get a summary of Account activity, or an individual Endpoint """
    activity = controller.describe_activity(days=days, endpoint_id=endpoint_id)
    print_json(data=activity)
