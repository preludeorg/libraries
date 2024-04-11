import click
from rich import print_json

from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.partner_controller import PartnerController
from prelude_sdk.models.codes import Control


@click.group()
@click.pass_context
def partner(ctx):
    """ Partner system commands """
    ctx.obj = PartnerController(account=ctx.obj)


@partner.command('attach')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('--api', required=True, help='API endpoint of the partner')
@click.option('--user', default='', help='user identifier')
@click.option('--secret', default='', help='secret for OAUTH use cases')
@click.pass_obj
@handle_api_error
def attach_partner(controller, partner, api, user, secret):
    """ Attach an EDR to Detect """
    with Spinner(description='Attaching partner'):
        data = controller.attach(partner=Control[partner], api=api, user=user, secret=secret)
    print_json(data=data)


@partner.command('detach')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.pass_obj
@handle_api_error
def detach_partner(controller, partner):
    """ Detach an existing partner from your account """
    with Spinner(description='Detaching partner'):
        data = controller.detach(partner=Control[partner])
    print_json(data=data)


@partner.command('block')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('-t', '--test_id', required=True, help='a test to block')
@click.pass_obj
@handle_api_error
def partner_block(controller, partner, test_id):
    """ Report to a partner to block a test """
    with Spinner(description='Reporting test to partner'):
        data = controller.block(partner=Control[partner], test_id=test_id)
    print_json(data=data)


@partner.command('endpoints')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('--platform', required=True, help='platform name (e.g. "windows")', type=click.Choice(['windows', 'linux', 'darwin'], case_sensitive=False))
@click.option('--hostname', default='', help='hostname pattern (e.g. "mycompany-c24oi444")')
@click.option('--offset', default=0, help='API pagination offset', type=int)
@click.option('--limit', default=100, help='API pagination limit', type=int)
@click.pass_obj
@handle_api_error
def partner_endpoints(controller, partner, platform, hostname, offset, limit):
    """ Get a list of endpoints from a partner """
    with Spinner(description='Fetching endpoints from partner'):
        data = controller.endpoints(partner=Control[partner], platform=platform, hostname=hostname, offset=offset, count=limit)
    print_json(data=data)


@partner.command('deploy')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('--host_ids', required=True, help='a list of host IDs to deploy to', multiple=True, default=[])
@click.pass_obj
@handle_api_error
def partner_deploy(controller, partner, host_ids):
    """ Deploy probes to hosts associated to a partner """
    with Spinner(description='Deploying probes to hosts'):
        data = controller.deploy(partner=Control[partner], host_ids=host_ids)
    print_json(data=data)


@partner.command('generate-webhook')
@click.argument('partner', type=click.Choice(['DEFENDER', 'SENTINELONE', 'CROWDSTRIKE'], case_sensitive=False))
@click.pass_obj
@handle_api_error
def generate_webhook(controller, partner):
    """ Generate webhook credentials for an EDR system to enable the forwarding of alerts to the Prelude API, facilitating automatic alert suppression """
    with Spinner(description='Generating webhook credentials'):
        data = controller.generate_webhook(partner=Control[partner])
    print_json(data=data)
    print("\nVisit https://docs.preludesecurity.com/docs/alert-management for details on configuring your EDR to forward alerts.\n")


@partner.command('reports')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-t', '--test_id', required=True, help='test to get reports for')
@click.pass_obj
@handle_api_error
def partner_reports(controller, partner, test_id):
    """ Get reports to a partner for a test """
    with Spinner(description='Getting reports to partner'):
        data = controller.list_reports(partner=Control[partner], test_id=test_id)
    print_json(data=data)
