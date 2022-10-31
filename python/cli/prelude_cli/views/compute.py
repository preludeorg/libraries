import click
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.compute_controller import ComputeController
from prelude_sdk.models.codes import Colors
from rich import print_json


@click.group()
@click.pass_context
def compute(ctx):
    """ Interact with your Compute server """
    ctx.obj = ComputeController(account=ctx.obj)


@compute.command('describe-server')
@click.pass_obj
@handle_api_error
def describe_server(controller):
    """ Locate your Compute server """
    private_ip = controller.describe_server()
    if private_ip:
        click.secho(f'Your Compute server is {private_ip}', fg=Colors.GREEN.value)
    print('Compute server booting up. Please try again in 30s.')


@compute.command('test-code')
@click.argument('name')
@click.pass_obj
@handle_api_error
def test_code(controller, name):
    """ Test a code file """
    print_json(controller.compute_proxy(route='test', name=name))


@compute.command('publish-code')
@click.argument('name')
@click.pass_obj
@handle_api_error
def publish_code(controller, name):
    """ Save compiled code file to DB """
    controller.compute_proxy(route='publish', name=name)
    print(f'{name} published')


@compute.command('create-url')
@click.argument('name')
@click.pass_obj
@handle_api_error
def create_url(controller, name):
    """ Generate deploy url """
    url = controller.create_url(name=name)
    print(url)
    click.secho(f'Use the above url to download {name}', fg=Colors.GREEN.value)
