import click
import requests
from time import sleep

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control, ControlCategory, PartnerEvents, RunCode, SCMCategory


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
@click.option('--instance_id', required=True, help='instance ID of the partner')
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('-q', '--techniques', help='comma-separated list of techniques to filter by', type=str, default=None)
@click.pass_obj
@pretty_print
def evaluation(controller, partner, instance_id, odata_filter, techniques):
    """ Get policy evaluation for given partner """
    with Spinner(description='Getting policy evaluation'):
        return controller.evaluation(partner=Control[partner], instance_id=instance_id, filter=odata_filter, techniques=techniques)

@scm.command('sync')
@click.argument('partner',
                type=click.Choice([c.name for c in Control if c != Control.INVALID], case_sensitive=False),
                required=True)
@click.option('--instance_id', required=True, help='instance ID of the partner')
@click.pass_obj
@pretty_print
def sync(controller, partner, instance_id):
    """ Update policy evaluation for given partner """
    with Spinner(description='Updating policy evaluation'):
        job_id = controller.update_evaluation(partner=Control[partner], instance_id=instance_id)['job_id']
        jobs = JobsController(account=controller.account)
        while (result := jobs.job_status(job_id))['end_time'] is None:
            sleep(3)
        return result
    
@scm.command('export')
@click.argument('type', type=click.Choice([c.name for c in SCMCategory if c.value > 0], case_sensitive=False))
@click.option('-o', '--output_file', help='csv filename to export to', type=click.Path(writable=True), required=True)
@click.option('--limit', default=100, help='maximum number of results to return', type=int)
@click.option('--odata_filter', help='OData filter string', default=None)
@click.option('--odata_orderby', help='OData orderby string', default=None)
@click.pass_obj
@pretty_print
def export(controller, type, output_file, limit, odata_filter, odata_orderby):
    """ Export SCM data """
    with Spinner(description='Exporting SCM data'):
        export = ExportController(account=controller.account)
        jobs = JobsController(account=controller.account)
        job_id = export.export_scm(export_type=SCMCategory[type], filter=odata_filter, orderby=odata_orderby, top=limit)['job_id']
        while (result := jobs.job_status(job_id))['end_time'] is None:
            sleep(3)
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
    with Spinner('Parsing PDF'):
        return controller.parse_threat_intel(threat_pdf)

@scm.command('from-advisory')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-a', '--advisory_id', required=True, type=str, help='Partner advisory ID')
@click.pass_obj
@pretty_print
def parse_from_partner_advisory(controller, partner, advisory_id):
    with Spinner('Uploading'):
        return controller.parse_from_partner_advisory(partner=Control[partner], advisory_id=advisory_id)

@scm.command('list-notifications')
@click.pass_obj
@pretty_print
def list_notifications(controller):
    with Spinner('Fetching notifications'):
        return controller.list_notifications()

@scm.command('delete-notification')
@click.argument('notification_id', type=str)
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@pretty_print
def delete_notification(controller, notification_id):
    with Spinner('Deleting notification'):
        return controller.delete_notification(notification_id)

@scm.command('upsert-notification')
@click.argument('control_category', type=click.Choice([c.name for c in ControlCategory], case_sensitive=False))
@click.option('-e', '--emails', help='comma-separated list of emails to notify', default=None, type=str)
@click.option('-v', '--event', help='event to trigger notification for', type=click.Choice([e.name for e in PartnerEvents], case_sensitive=False), required=True)
@click.option('-f', '--filter', help='OData filter string', default=None, type=str)
@click.option('-i', '--id', help='ID of the notification to update', default=None, type=str)
@click.option('-m', '--message', help='notification message', default='', type=str)
@click.option('-r', '--run_code', help='notification frequency', type=click.Choice([r.name for r in RunCode], case_sensitive=False), required=True)
@click.option('-s', '--scheduled_hour', help='scheduled hour to receive notifications', type=int, required=True)
@click.option('-u', '--slack_urls', help='comma-separated list of Slack Webhook URLs to notify', default=None, type=str)
@click.option('-t', '--title', help='notification title', default='SCM Notification', type=str)
@click.pass_obj
@pretty_print
def upsert_notification(controller, control_category, emails, event, filter, id, message, run_code, scheduled_hour, slack_urls, title):
    """ Upsert an SCM notification """
    with Spinner('Upserting notification'):
        return controller.upsert_notification(
            control_category=ControlCategory[control_category],
            emails=emails.split(',') if emails else None,
            event=PartnerEvents[event],
            filter=filter,
            id=id,
            message=message,
            run_code=RunCode[run_code],
            scheduled_hour=scheduled_hour,
            slack_urls=slack_urls.split(',') if slack_urls else None,
            title=title
        )
