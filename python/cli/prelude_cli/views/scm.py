import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control


@click.group()
@click.pass_context
def scm(ctx):
    """ SCM system commands """
    ctx.obj = ScmController(account=ctx.obj)

@scm.command('endpoints')
@click.option('--partner',
              type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), default=None)
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def endpoints(controller, partner, limit, odata_filter, odata_orderby):
    """ List endpoints with SCM data """
    with Spinner(description='Fetching endpoints from partner'):
        return controller.endpoints(partner=Control[partner] if partner else None, filter=odata_filter, orderby=odata_orderby, top=limit)

@scm.command('technique-summary')
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, required=True)
@click.pass_obj
@pretty_print
def technique_summary(controller, techniques):
    """ Get policy summary per technique """
    with Spinner(description='Getting policy summary by technique'):
        return controller.technique_summary(techniques=techniques)

@scm.command('evaluation-summary')
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def evaluation_summary(controller, techniques):
    """ Get policy evaluation summary for all partners """
    with Spinner(description='Getting policy evaluation summary'):
        return controller.evaluation_summary(techniques=techniques)
    
@scm.command('evaluation')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False))
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def evaluation(controller, partner, techniques):
    """ Get policy evaluation for given partner """
    with Spinner(description='Getting policy evaluation'):
        return controller.evaluation(partner=Control[partner], techniques=techniques)

@scm.command('sync')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False), required=False)
@click.pass_obj
@pretty_print
def sync(controller, partner):
    """ Update policy evaluation for given partner """
    with Spinner(description='Updating policy evaluation'):
        return controller.evaluation(partner=Control[partner])
    
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
        export = ExportController(account=controller.account)
        data = export.export_scm(export_type=type, filter=odata_filter, orderby=odata_orderby, partner=Control[partner] if partner else None, top=limit)
        with open(output_file, 'wb') as f:
            f.write(data)
        return dict(status=True), f'Exported data to {output_file}'

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
