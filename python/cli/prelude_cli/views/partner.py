import click

from rich import print_json

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.partner_controller import PartnerController


@click.group()
@click.pass_context
def partner(ctx):
    """ Partner system commands """
    ctx.obj = PartnerController(account=ctx.obj)


@partner.command('endpoints')
@click.option('--name', required=True, help='partner name (e.g. "CrowdStrike")')
@click.option('--platform', required=True, help='platform name (e.g. "windows")', type=click.Choice(['windows', 'linux', 'darwin'], case_sensitive=False))
@click.option('--hostname', default='', help='hostname pattern (e.g. "mycompany-c24oi444")')
@click.option('--offset', default=0, help='API pagination offset', type=int)
@click.pass_obj
@handle_api_error
def partner_endpoints(controller, name, platform, hostname, offset):
    """ Get a list of endpoints from all partners """
    print_json(data=controller.endpoints(partner_name=name, platform=platform, hostname=hostname, offset=offset))


@partner.command('deploy')
@click.confirmation_option(prompt='Are you sure?')
@click.option('--name', required=True, help='partner name (e.g. "CrowdStrike")')
@click.option('--host_ids', required=True, help='a list of host IDs to deploy to', multiple=True, default=[])
@click.pass_obj
@handle_api_error
def partner_deploy(controller, name, host_ids):
    """ Deploy probes to hosts associated to a partner """
    print_json(data=controller.deploy(partner_name=name, host_ids=host_ids))
