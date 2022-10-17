import click
from rich import print_json

from detect_sdk.controllers.endpoint_controller import EndpointController
from detect_sdk.models.codes import Colors
from detect_cli.views.shared import handle_api_error


@click.group()
@click.pass_context
def endpoint(ctx):
    """ Manage your endpoints """
    ctx.obj = EndpointController(account=ctx.obj)


@endpoint.command('register')
@click.option('--tag', help='add a custom tag to this endpoint')
@click.argument('name')
@click.pass_obj
@handle_api_error
def register_endpoint(controller, name, tag):
    """Register a new endpoint"""
    endpoint_token = controller.register_endpoint(name=name, tag=tag)
    click.secho('Endpoint token: %s' % endpoint_token, fg=Colors.GREEN.value)


@endpoint.command('activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.argument('endpoint_id')
@click.pass_obj
@handle_api_error
def describe_activity(controller, endpoint_id, days):
    """ Get a results for a specific endpoint """
    activity = controller.describe_activity(days=days, endpoint_id=endpoint_id)
    print_json(data=activity)
