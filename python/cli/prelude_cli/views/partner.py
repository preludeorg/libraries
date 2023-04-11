import click

from rich import print_json

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.partner_controller import PartnerController


@click.group()
@click.pass_context
def partner(ctx):
    """ Continuous security testing """
    ctx.obj = PartnerController(account=ctx.obj)


@detect.command('partner-endpoints')
@click.option('--control_name', required=True, help='control name (e.g. "CrowdStrike")')
@click.option('--platform', required=True, help='platform name (e.g. "windows")')
@click.option('--hostname', default='', help='hostname pattern (e.g. "mycompany-c24oi444")')
@click.option('--offset', default=0, help='API pagination offset', type=int)
@click.pass_obj
@handle_api_error
def partner_endpoints(controller, control_name, platform, hostname, offset):
    """ Get a list of endpoints from all partners """
    print_json(controller.partner_endpoints(control_name=control_name, platform=platform, hostname=hostname, offset=offset))


@detect.command('partner-deploy')
@click.confirmation_option(prompt='Are you sure?')
@click.option('--control_name', required=True, help='control name (e.g. "CrowdStrike")')
@click.option('--host_ids', required=True, help='a list of host IDs to deploy to', type=list[str])
@click.pass_obj
@handle_api_error
def detach_partner(controller, control_name, host_ids):
    """ Detach an existing partner from your account """
    controller.partner_deploy(control_name=control_name, host_ids=host_ids)
