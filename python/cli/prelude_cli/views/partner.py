import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.export_controller import ExportController
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
@pretty_print
def attach_partner(controller, partner, api, user, secret):
    """ Attach an EDR to Detect """
    with Spinner(description='Attaching partner'):
        return controller.attach(partner=Control[partner], api=api, user=user, secret=secret)

@partner.command('detach')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.pass_obj
@pretty_print
def detach_partner(controller, partner):
    """ Detach an existing partner from your account """
    with Spinner(description='Detaching partner'):
        return controller.detach(partner=Control[partner])

@partner.command('block')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('-t', '--test_id', required=True, help='a test to block')
@click.pass_obj
@pretty_print
def partner_block(controller, partner, test_id):
    """ Report to a partner to block a test """
    with Spinner(description='Reporting test to partner'):
        return controller.block(partner=Control[partner], test_id=test_id)

@partner.command('endpoints')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('--platform', help='platform name (e.g. "windows")', required=True, type=click.Choice(['windows', 'linux', 'darwin'], case_sensitive=False))
@click.option('--hostname', default='', help='hostname pattern (e.g. "mycompany-c24oi444")')
@click.option('--offset', default=0, help='API pagination offset', type=int)
@click.option('--limit', default=100, help='API pagination limit', type=int)
@click.pass_obj
@pretty_print
def partner_endpoints(controller, partner, platform, hostname, offset, limit):
    """ Get a list of endpoints from a partner """
    with Spinner(description='Fetching endpoints from partner'):
        return controller.endpoints(partner=Control[partner], platform=platform, hostname=hostname, offset=offset, count=limit)

@partner.command('deploy')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('--host_ids', required=True, help='a list of host IDs to deploy to', multiple=True, default=[])
@click.pass_obj
@pretty_print
def partner_deploy(controller, partner, host_ids):
    """ Deploy probes to hosts associated to a partner """
    with Spinner(description='Deploying probes to hosts'):
        return controller.deploy(partner=Control[partner], host_ids=host_ids)

@partner.command('generate-webhook')
@click.argument('partner', type=click.Choice(['DEFENDER', 'SENTINELONE', 'CROWDSTRIKE'], case_sensitive=False))
@click.pass_obj
@pretty_print
def generate_webhook(controller, partner):
    """ Generate webhook credentials for an EDR system to enable the forwarding of alerts to the Prelude API, facilitating automatic alert suppression """
    with Spinner(description='Generating webhook credentials'):
        return controller.generate_webhook(partner=Control[partner])

@partner.command('reports')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-t', '--test_id', help='test to get reports for')
@click.pass_obj
@pretty_print
def partner_reports(controller, partner, test_id):
    """ Get reports to a partner for a test """
    with Spinner(description='Getting reports to partner'):
        return controller.list_reports(partner=Control[partner], test_id=test_id)

@partner.command('ioa-stats')
@click.option('-t', '--test_id', help='test to get IOA stats for')
@click.pass_obj
@pretty_print
def ioa_stats(controller, test_id):
    """ Get IOA stats """
    with Spinner(description='Getting IOA stats'):
        return controller.ioa_stats(test_id=test_id)

@partner.command('observed-detected')
@click.option('-t', '--test_id', help='test to get observed/detected stats for')
@click.option('-h', '--hours', help='number of hours to look back', type=int)
@click.pass_obj
@pretty_print
def observed_detected(controller, test_id, hours):
    """ Get observed / detected stats """
    with Spinner(description='Getting observed / detected stats'):
        return controller.observed_detected(test_id=test_id, hours=hours)

@partner.command('advisories')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-s', '--start', help='start date for advisories')
@click.option('-o', '--offset', help='API pagination offset', type=int)
@click.option('-l', '--limit', help='API pagination limit', type=int)
@click.pass_obj
@pretty_print
def partner_advisories(controller, partner, start, offset, limit):
    """ Get advisories provided by partner """
    with Spinner(description='Getting partner advisories'):
        return controller.list_advisories(partner=Control[partner], start=start, offset=offset, limit=limit)

## --------- SCM Commands --------- ##


@partner.command('scm-endpoints')
@click.option('--partner',
              type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), default=None)
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def scm_endpoints(controller, partner, limit, odata_filter, odata_orderby):
    """ Get a list of endpoints with SCM data """
    with Spinner(description='Fetching endpoints from partner'):
        return controller.endpoints_via_scm(partner=Control[partner] if partner else None, filter=odata_filter, orderby=odata_orderby, top=limit)

@partner.command('scm-summary')
@click.option('-t', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def scm_summary(controller, techniques):
    """ Get policy evaluation summary for all partners """
    with Spinner(description='Getting policy evaluation summary'):
        return controller.get_policy_evaluation_summary(techniques=techniques)
    
@partner.command('scm-evaluation')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('-t', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def scm_evaluation(controller, partner, techniques):
    """ Get policy evaluations for given partner """
    with Spinner(description='Getting policy evaluations'):
        return controller.get_policy_evaluation(partner=Control[partner], techniques=techniques)

@partner.command('sync-scm')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), required=False)
@click.pass_obj
@pretty_print
def sync_scm(controller, partner):
    """ Update policy evaluations for given partner """
    with Spinner(description='Updating policy evaluations'):
        return controller.update_policy_evaluation(partner=Control[partner])
    
@partner.command('export-scm')
@click.argument('type', type=click.Choice(['endpoints', 'inboxes', 'users'], case_sensitive=False))
@click.option('-o', '--output_file', help='csv filename to export to', type=click.Path(writable=True), required=True)
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.option('--partner',
              type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), default=None)
@click.pass_obj
@pretty_print
def export_scm(controller, type, output_file, limit, odata_filter, odata_orderby, partner):
    """ Export SCM data """
    with Spinner(description='Exporting SCM data'):
        export = ExportController(account=controller.account)
        data = export.partner(export_type=type, filter=odata_filter, orderby=odata_orderby, partner=Control[partner] if partner else None, top=limit)
        with open(output_file, 'wb') as f:
            f.write(data)
        return dict(status=True), f'Exported data to {output_file}'

@partner.command('create-scm-threat', hidden=True)
@click.argument('name')
@click.option('-d', '--description', help='description of the threat', default=None, type=str)
@click.option('-p', '--published', help='date the threat was published', default=None, type=str)
@click.option('-q', '--techniques', help='comma-separated list of techniques (MITRE ATT&CK IDs)', default=None, type=str)
@click.pass_obj
@pretty_print
def create_scm_threat(controller, name, description, published, techniques):
    """ Create an scm threat """
    with Spinner(description='Creating scm threat'):
        return controller.create_scm_threat(name=name, description=description, published=published, techniques=techniques)

@partner.command('delete-scm-threat', hidden=True)
@click.argument('threat')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@pretty_print
def delete_scm_threat(controller, threat):
    """ Delete an scm threat """
    with Spinner(description='Removing scm threat'):
        return controller.delete_scm_threat(name=threat)

@partner.command('list-scm-threats', hidden=True)
@click.pass_obj
@pretty_print
def list_scm_threats(controller):
    """ List all scm threats """
    with Spinner(description='Fetching scm threats'):
        return controller.list_scm_threats()
