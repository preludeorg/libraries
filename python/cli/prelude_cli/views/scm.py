import click
import requests
from time import sleep

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control


@click.group()
@click.pass_context
def scm(ctx):
    """ SCM system commands """
    ctx.obj = ScmController(account=ctx.obj)

@scm.command('endpoints')
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def endpoints(controller, limit, odata_filter, odata_orderby):
    """ List endpoints with SCM data """
    with Spinner(description='Fetching endpoints from partner'):
        return controller.endpoints(filter=odata_filter, orderby=odata_orderby, top=limit)

@scm.command('inboxes')
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def endpoints(controller, limit, odata_filter, odata_orderby):
    """ List inboxes with SCM data """
    with Spinner(description='Fetching inboxes from partner'):
        return controller.inboxes(filter=odata_filter, orderby=odata_orderby, top=limit)

@scm.command('users')
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def endpoints(controller, limit, odata_filter, odata_orderby):
    """ List users with SCM data """
    with Spinner(description='Fetching users from partner'):
        return controller.users(filter=odata_filter, orderby=odata_orderby, top=limit)

@scm.command('technique-summary')
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, required=True)
@click.pass_obj
@pretty_print
def technique_summary(controller, techniques):
    """ Get policy summary per technique """
    with Spinner(description='Getting policy summary by technique'):
        return controller.technique_summary(techniques=techniques)

@scm.command('evaluation-summary')
@click.option('--endpoint_odata_filter', help='OData filter string for endpoints', default=None)
@click.option('--inbox_odata_filter', help='OData filter string for inboxes', default=None)
@click.option('--user_odata_filter', help='OData filter string for users', default=None)
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def evaluation_summary(controller, endpoint_odata_filter, inbox_odata_filter, user_odata_filter, techniques):
    """ Get policy evaluation summary for all partners """
    with Spinner(description='Getting policy evaluation summary'):
        return controller.evaluation_summary(
            endpoint_filter=endpoint_odata_filter,
            inbox_filter=inbox_odata_filter,
            user_filter=user_odata_filter,
            techniques=techniques
        )
    
@scm.command('evaluation')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def evaluation(controller, partner, odata_filter, techniques):
    """ Get policy evaluation for given partner """
    with Spinner(description='Getting policy evaluation'):
        return controller.evaluation(partner=Control[partner], filter=odata_filter, techniques=techniques)

@scm.command('sync')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False),
                required=True)
@click.pass_obj
@pretty_print
def sync(controller, partner):
    """ Update policy evaluation for given partner """
    with Spinner(description='Updating policy evaluation'):
        job_id = controller.update_evaluation(partner=Control[partner])['job_id']
        detect = DetectController(account=controller.account)
        while (result := detect.get_background_job(job_id))['end_time'] is None:
            sleep(3)
            pass
        return result
    
@scm.command('export')
@click.argument('type', type=click.Choice(['endpoints', 'inboxes', 'users'], case_sensitive=False))
@click.option('-o', '--output_file', help='csv filename to export to', type=click.Path(writable=True), required=True)
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.option('--partner',
              type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), default=None)
@click.pass_obj
@pretty_print
def export(controller, type, output_file, limit, odata_filter, odata_orderby, partner):
    """ Export SCM data """
    with Spinner(description='Exporting SCM data'):
        detect = DetectController(account=controller.account)
        export = ExportController(account=controller.account)
        job_id = export.export_scm(export_type=type, filter=odata_filter, orderby=odata_orderby, partner=Control[partner] if partner else None, top=limit)['job_id']
        while (result := detect.get_background_job(job_id))['end_time'] is None:
            sleep(3)
            pass
        if result['successful']:
            data = requests.get(result['results']['url'], timeout=10).content
            with open(output_file, 'wb') as f:
                f.write(data)
        return result, f'Exported data to {output_file}'

@scm.command('create-scm-threat', hidden=True)
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

@scm.command('delete-scm-threat', hidden=True)
@click.argument('threat')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@pretty_print
def delete_scm_threat(controller, threat):
    """ Delete an scm threat """
    with Spinner(description='Removing scm threat'):
        return controller.delete_scm_threat(name=threat)

@scm.command('list-scm-threats', hidden=True)
@click.pass_obj
@pretty_print
def list_scm_threats(controller):
    """ List all scm threats """
    with Spinner(description='Fetching scm threats'):
        return controller.list_scm_threats()

@scm.command('threat-intel')
@click.argument('threat_pdf', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.pass_obj
@pretty_print
def parse_threat_intel(controller, threat_pdf):
    with Spinner('Parsing PDF') as spinner:
        return controller.parse_threat_intel(threat_pdf)

@scm.command('from-advisory')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-a', '--advisory_id', required=True, type=str, help='Partner advisory ID')
@click.pass_obj
@pretty_print
def parse_from_partner_advisory(controller, partner, advisory_id):
    with Spinner('Uploading') as spinner:
        return controller.parse_from_partner_advisory(partner=Control[partner], advisory_id=advisory_id)
