import click

from rich import print_json

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.partner_controller import PartnerController


@click.group()
@click.pass_context
def partner(ctx):
    """ Continuous security testing """
    ctx.obj = PartnerController(account=ctx.obj)


@partner.command('endpoints')
@click.option('--partner_name', required=True, help='control name (e.g. "CrowdStrike")')
@click.option('--platform', required=True, help='platform name (e.g. "windows")', type=click.Choice(['windows', 'linux', 'darwin'], case_sensitive=False))
@click.option('--hostname', default='', help='hostname pattern (e.g. "mycompany-c24oi444")')
@click.option('--offset', default=0, help='API pagination offset', type=int)
@click.pass_obj
@handle_api_error
def partner_endpoints(controller, partner_name, platform, hostname, offset):
    """ Get a list of endpoints from all partners """
    print_json(controller.partner_endpoints(partner_name=partner_name, platform=platform, hostname=hostname, offset=offset))


@partner.command('deploy')
@click.confirmation_option(prompt='Are you sure?')
@click.option('--partner_name', required=True, help='control name (e.g. "CrowdStrike")')
@click.option('--host_ids', required=True, help='a list of host IDs to deploy to', type=list[str])
@click.pass_obj
@handle_api_error
def detach_partner(controller, partner_name, host_ids):
    """ Detach an existing partner from your account """
    controller.partner_deploy(partner_name=partner_name, host_ids=host_ids)
