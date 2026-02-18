import click
import json
import requests
from time import sleep

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import (
    Control,
    ControlCategory,
    PartnerEvents,
    PolicyType,
    RunCode,
    SCMCategory,
)


@click.group()
@click.pass_context
def scm(ctx):
    """SCM system commands"""
    ctx.obj = ScmController(account=ctx.obj)


@scm.command("endpoints")
@click.option(
    "--limit", default=100, help="maximum number of results to return", type=int
)
@click.option("--offset", default=0, help="number of results to skip", type=int)
@click.option(
    "--odata_select", help="OData select string to specify which fields to return"
)
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def endpoints(controller, limit, offset, odata_select, odata_filter, odata_orderby):
    """List endpoints with SCM data"""
    with Spinner(description="Fetching endpoints from partner"):
        return controller.endpoints(
            select=odata_select,
            filter=odata_filter,
            orderby=odata_orderby,
            top=limit,
            skip=offset,
        )


@scm.command("inboxes")
@click.option(
    "--limit", default=100, help="maximum number of results to return", type=int
)
@click.option("--offset", default=0, help="number of results to skip", type=int)
@click.option(
    "--odata_select", help="OData select string to specify which fields to return"
)
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def inboxes(controller, limit, offset, odata_select, odata_filter, odata_orderby):
    """List inboxes with SCM data"""
    with Spinner(description="Fetching inboxes from partner"):
        return controller.inboxes(
            select=odata_select,
            filter=odata_filter,
            orderby=odata_orderby,
            top=limit,
            skip=offset,
        )


@scm.command("network_devices")
@click.option(
    "--limit", default=100, help="maximum number of results to return", type=int
)
@click.option("--offset", default=0, help="number of results to skip", type=int)
@click.option(
    "--odata_select", help="OData select string to specify which fields to return"
)
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def network_devices(
    controller, limit, offset, odata_select, odata_filter, odata_orderby
):
    """List network devices with SCM data"""
    with Spinner(description="Fetching network devices from partner"):
        return controller.network_devices(
            select=odata_select,
            filter=odata_filter,
            orderby=odata_orderby,
            top=limit,
            skip=offset,
        )


@scm.command("users")
@click.option(
    "--limit", default=100, help="maximum number of results to return", type=int
)
@click.option("--offset", default=0, help="number of results to skip", type=int)
@click.option(
    "--odata_select", help="OData select string to specify which fields to return"
)
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def users(controller, limit, offset, odata_select, odata_filter, odata_orderby):
    """List users with SCM data"""
    with Spinner(description="Fetching users from partner"):
        return controller.users(
            select=odata_select,
            filter=odata_filter,
            orderby=odata_orderby,
            top=limit,
            skip=offset,
        )


@scm.command("technique-summary")
@click.option(
    "-q",
    "--techniques",
    help="comma-separated list of techniques to filter by",
    required=True,
)
@click.pass_obj
@pretty_print
def technique_summary(controller, techniques):
    """Get policy summary per technique"""
    with Spinner(description="Getting policy summary by technique"):
        return controller.technique_summary(techniques=techniques)


@scm.command("evaluation-summary")
@click.option(
    "--endpoint_odata_filter",
    help="OData filter string for endpoints",
)
@click.option(
    "--inbox_odata_filter",
    help="OData filter string for inboxes",
)
@click.option("--user_odata_filter", help="OData filter string for users")
@click.option(
    "-q", "--techniques", help="comma-separated list of techniques to filter by"
)
@click.pass_obj
@pretty_print
def evaluation_summary(
    controller, endpoint_odata_filter, inbox_odata_filter, user_odata_filter, techniques
):
    """Get policy evaluation summary for all partners"""
    with Spinner(description="Getting policy evaluation summary"):
        return controller.evaluation_summary(
            endpoint_filter=endpoint_odata_filter,
            inbox_filter=inbox_odata_filter,
            user_filter=user_odata_filter,
            techniques=techniques,
        )


@scm.command("evaluation")
@click.argument(
    "partner",
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
)
@click.option("--instance_id", required=True, help="instance ID of the partner")
@click.option("--odata_filter", help="OData filter string")
@click.option(
    "-p",
    "--policy_type",
    default=[],
    help="Policy types to filter by",
    multiple=True,
    type=click.Choice(
        [p.name for p in PolicyType if p != PolicyType.INVALID], case_sensitive=False
    ),
)
@click.option(
    "-q", "--techniques", help="comma-separated list of techniques to filter by"
)
@click.pass_obj
@pretty_print
def evaluation(controller, partner, instance_id, odata_filter, policy_type, techniques):
    """Get policy evaluation for given partner"""
    with Spinner(description="Getting policy evaluation"):
        return controller.evaluation(
            partner=Control[partner],
            instance_id=instance_id,
            filter=odata_filter,
            policy_types=",".join(policy_type),
            techniques=techniques,
        )


@scm.command("sync")
@click.argument(
    "partner",
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
    required=True,
)
@click.option("--instance_id", required=True, help="instance ID of the partner")
@click.pass_obj
@pretty_print
def sync(controller, partner, instance_id):
    """Update policy evaluation for given partner"""
    with Spinner(description="Updating policy evaluation"):
        job_id = controller.update_evaluation(
            partner=Control[partner], instance_id=instance_id
        )["job_id"]
        jobs = JobsController(account=controller.account)
        while (result := jobs.job_status(job_id))["end_time"] is None:
            sleep(3)
        return result


@scm.command("export")
@click.argument(
    "type",
    type=click.Choice(
        [c.name for c in SCMCategory if c.value > 0], case_sensitive=False
    ),
)
@click.option(
    "-o",
    "--output_file",
    help="csv filename to export to",
    type=click.Path(writable=True),
    required=True,
)
@click.option("--limit", help="maximum number of results to return", type=int)
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def export(controller, type, output_file, limit, odata_filter, odata_orderby):
    """Export SCM data"""
    with Spinner(description="Exporting SCM data"):
        export = ExportController(account=controller.account)
        jobs = JobsController(account=controller.account)
        job_id = export.export_scm(
            export_type=SCMCategory[type],
            filter=odata_filter,
            orderby=odata_orderby,
            top=limit,
        )["job_id"]
        while (result := jobs.job_status(job_id))["end_time"] is None:
            sleep(3)
        if result["successful"]:
            data = requests.get(result["results"]["url"], timeout=10).content
            with open(output_file, "wb") as f:
                f.write(data)
        return result, f"Exported data to {output_file}"


@click.group()
@click.pass_context
def group(ctx):
    """SCM group commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


scm.add_command(group)


@group.command("list")
@click.option("--odata_filter", help="OData filter string")
@click.option("--odata_orderby", help="OData orderby string")
@click.pass_obj
@pretty_print
def list_partner_groups(controller, odata_filter, odata_orderby):
    """List all partner groups"""
    with Spinner(description="Fetching partner groups"):
        return controller.list_partner_groups(
            filter=odata_filter, orderby=odata_orderby
        )


@group.command("sync")
@click.argument(
    "partner",
    required=True,
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
)
@click.option("--instance_id", help="instance ID of the partner", required=True)
@click.option("--group_ids", help="comma-separated list of group IDs", required=True)
@click.pass_obj
@pretty_print
def sync_groups(controller, partner, instance_id, group_ids):
    """Update groups for a partner"""
    with Spinner(description="Updating groups"):
        job_id = controller.update_partner_groups(
            partner=Control[partner],
            instance_id=instance_id,
            group_ids=group_ids.split(","),
        )["job_id"]
        jobs = JobsController(account=controller.account)
        while (result := jobs.job_status(job_id))["end_time"] is None:
            sleep(3)
        return result


@click.group()
@click.pass_context
def threat(ctx):
    """SCM threat commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


scm.add_command(threat)


@threat.command("create")
@click.argument("name")
@click.option("-d", "--description", help="description of the threat")
@click.option("--id", help="uuid for threat")
@click.option(
    "-g", "--generated", default=False, help="was the threat AI generated", type=bool
)
@click.option("-p", "--published", help="date the threat was published")
@click.option("-s", "--source", help="source of threat (ex. www.cisa.gov)")
@click.option(
    "-i", "--source_id", help="ID of the threat, per the source (ex. aa23-075a)"
)
@click.option(
    "-q", "--techniques", help="comma-separated list of techniques (MITRE ATT&CK IDs)"
)
@click.pass_obj
@pretty_print
def create_threat(
    controller,
    name,
    description,
    id,
    generated,
    published,
    source,
    source_id,
    techniques,
):
    """Create an scm threat"""
    with Spinner(description="Creating scm threat"):
        return controller.create_threat(
            name=name,
            description=description,
            id=id,
            generated=generated,
            published=published,
            source=source,
            source_id=source_id,
            techniques=techniques,
        )


@threat.command("delete")
@click.argument("threat_id")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def delete_threat(controller, threat_id):
    """Delete an scm threat"""
    with Spinner(description="Removing scm threat"):
        return controller.delete_threat(id=threat_id)


@threat.command("list")
@click.pass_obj
@pretty_print
def list_threats(controller):
    """List all scm threats"""
    with Spinner(description="Fetching scm threats"):
        return controller.list_threats()


@threat.command("get")
@click.argument("threat_id")
@click.pass_obj
@pretty_print
def get_threat(controller, threat_id):
    """Get specific scm threat"""
    with Spinner(description="Fetching scm threat"):
        return controller.get_threat(id=threat_id)


@scm.command("threat-intel")
@click.argument(
    "threat_pdf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.pass_obj
@pretty_print
def parse_threat_intel(controller, threat_pdf):
    with Spinner("Parsing PDF"):
        return controller.parse_threat_intel(threat_pdf)


@scm.command("from-advisory")
@click.argument(
    "partner", type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False)
)
@click.option("-a", "--advisory_id", help="Partner advisory ID", required=True)
@click.pass_obj
@pretty_print
def parse_from_partner_advisory(controller, partner, advisory_id):
    with Spinner("Uploading"):
        return controller.parse_from_partner_advisory(
            partner=Control[partner], advisory_id=advisory_id
        )


@click.group()
@click.pass_context
def exception(ctx):
    """SCM exception commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


@click.group()
@click.pass_context
def object(ctx):
    """SCM object exception commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


@click.group()
@click.pass_context
def policy(ctx):
    """SCM policy exception commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


exception.add_command(object)
exception.add_command(policy)
scm.add_command(exception)


@object.command("list")
@click.pass_obj
@pretty_print
def list_object_exceptions(controller):
    """List all object exceptions"""
    with Spinner(description="Fetching object exceptions"):
        return controller.list_object_exceptions()


@object.command("create")
@click.argument(
    "category",
    type=click.Choice(
        [
            c.name
            for c in ControlCategory
            if c
            not in [
                ControlCategory.NONE,
                ControlCategory.INVALID,
                ControlCategory.PRIVATE_REPO,
            ]
        ],
        case_sensitive=False,
    ),
)
@click.option("-f", "--filter", help="OData filter string", required=True)
@click.option("-c", "--comment", help="exception comment")
@click.option("-e", "--expires", help="expiry date (YYYY-MM-DD hh:mm:ss ([+-]hh:mm))")
@click.option(
    "-n",
    "--name",
    help="exception name",
)
@click.pass_obj
@pretty_print
def create_object_exception(controller, category, filter, comment, expires, name):
    """Create object exception"""
    with Spinner(description=f"Creating object exception"):
        return controller.create_object_exception(
            category=ControlCategory[category],
            comment=comment,
            filter=filter,
            name=name,
            expires=expires,
        )


@object.command("update")
@click.argument("exception_id")
@click.option("-c", "--comment", help="exception comment", default=None, type=str)
@click.option(
    "-e",
    "--expires",
    default=ScmController.default,
    help="Expiry Date (YYYY-MM-DD hh:mm:ss ([+-]hh:mm))",
)
@click.option("-f", "--filter", help="OData filter string")
@click.option("-n", "--name", help="Exception Name")
@click.pass_obj
@pretty_print
def update_object_exception(controller, exception_id, comment, expires, filter, name):
    """Update object exception"""
    with Spinner(description=f"Updating object exception"):
        return controller.update_object_exception(
            comment=comment,
            exception_id=exception_id,
            filter=filter,
            name=name,
            expires=expires,
        )


@object.command("delete")
@click.argument("exception_id")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def delete_object_exception(controller, exception_id):
    """Delete object exception"""
    with Spinner(description=f"Delete object exception"):
        return controller.delete_object_exception(exception_id=exception_id)


@policy.command("list")
@click.pass_obj
@pretty_print
def list_policy_exceptions(controller):
    """List all policy exceptions"""
    with Spinner(description="Fetching policy exceptions"):
        return controller.list_policy_exceptions()


@policy.command("create")
@click.argument(
    "partner",
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
)
@click.option("-c", "--comment", help="exception comment")
@click.option("-i", "--instance_id", help="instance ID of the partner", required=True)
@click.option("-p", "--policy_id", help="ID of the policy to create", required=True)
@click.option(
    "-s",
    "--settings",
    required=True,
    help="Comma separated list of all setting names to be excluded",
)
@click.option("-e", "--expires", help="Expiry Date (YYYY-MM-DD hh:mm:ss ([+-]hh:mm))")
@click.pass_obj
@pretty_print
def create_policy_exception(
    controller, partner, comment, instance_id, policy_id, settings, expires
):
    """Create policy exception"""
    with Spinner(description=f"Creating policy exception"):
        return controller.create_policy_exception(
            partner=Control[partner],
            comment=comment,
            expires=expires,
            instance_id=instance_id,
            policy_id=policy_id,
            setting_names=settings.split(",") if settings else None,
        )


@policy.command("update")
@click.argument(
    "partner",
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
)
@click.option("-c", "--comment", help="exception comment")
@click.option("-i", "--instance_id", help="instance ID of the partner", required=True)
@click.option("-p", "--policy_id", help="ID of the policy to update", required=True)
@click.option(
    "-e",
    "--expires",
    default=ScmController.default,
    help="Expiry Date (YYYY-MM-DD hh:mm:ss ([+-]hh:mm))",
)
@click.option(
    "-s", "--settings", help="Comma separated list of all setting names to be excluded"
)
@click.pass_obj
@pretty_print
def update_policy_exception(
    controller, partner, comment, instance_id, policy_id, expires, settings
):
    """Update policy exception"""
    with Spinner(description=f"Updating Policy exception"):
        return controller.update_policy_exception(
            partner=Control[partner],
            comment=comment,
            expires=expires,
            instance_id=instance_id,
            policy_id=policy_id,
            setting_names=settings.split(",") if settings else None,
        )


@policy.command("delete")
@click.argument(
    "partner",
    type=click.Choice(
        [c.name for c in Control if c != Control.INVALID], case_sensitive=False
    ),
)
@click.option("-i", "--instance_id", help="instance ID of the partner", required=True)
@click.option("-p", "--policy_id", help="ID of the policy to be deleted", required=True)
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def delete_policy_exception(controller, partner, instance_id, policy_id):
    """Delete policy exception"""
    with Spinner(description=f"Deleting Policy exception"):
        return controller.delete_policy_exception(
            instance_id=instance_id, policy_id=policy_id
        )


@click.group()
@click.pass_context
def notification(ctx):
    """SCM notification commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


scm.add_command(notification)


@notification.command("list")
@click.pass_obj
@pretty_print
def list_notifications(controller):
    with Spinner("Fetching notifications"):
        return controller.list_notifications()


@notification.command("delete")
@click.argument("notification_id")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def delete_notification(controller, notification_id):
    with Spinner("Deleting notification"):
        return controller.delete_notification(notification_id)


@notification.command("upsert")
@click.argument(
    "control_category",
    type=click.Choice([c.name for c in ControlCategory], case_sensitive=False),
)
@click.option(
    "-d",
    "--days_in_event",
    default=0,
    help="filter for results that have been in the event state for at least this many days",
    type=int,
)
@click.option("-e", "--emails", help="comma-separated list of emails to notify")
@click.option(
    "-v",
    "--event",
    help="event to trigger notification for",
    type=click.Choice([e.name for e in PartnerEvents], case_sensitive=False),
    required=True,
)
@click.option("-f", "--filter", help="OData filter string")
@click.option("-i", "--id", help="ID of the notification to update")
@click.option("-m", "--message", default="", help="notification message")
@click.option(
    "-r",
    "--run_code",
    help="notification frequency",
    type=click.Choice([r.name for r in RunCode], case_sensitive=False),
    required=True,
)
@click.option(
    "-s",
    "--scheduled_hour",
    help="scheduled UTC hour to receive notifications",
    type=int,
    required=True,
)
@click.option(
    "--slack_urls", help="comma-separated list of Slack Webhook URLs to notify"
)
@click.option(
    "-p",
    "--suppress_empty",
    help="suppress notifications with no results",
    default=True,
    type=bool,
)
@click.option(
    "--teams_urls", help="comma-separated list of Teams Webhook URLs to notify"
)
@click.option("-t", "--title", default="SCM Notification", help="notification title")
@click.pass_obj
@pretty_print
def upsert_notification(
    controller,
    control_category,
    days_in_event,
    emails,
    event,
    filter,
    id,
    message,
    run_code,
    scheduled_hour,
    slack_urls,
    suppress_empty,
    teams_urls,
    title,
):
    """Upsert an SCM notification"""
    with Spinner("Upserting notification"):
        return controller.upsert_notification(
            control_category=ControlCategory[control_category],
            days_in_event=days_in_event,
            emails=emails.split(",") if emails else None,
            event=PartnerEvents[event],
            filter=filter,
            id=id,
            message=message,
            run_code=RunCode[run_code],
            scheduled_hour=scheduled_hour,
            slack_urls=slack_urls.split(",") if slack_urls else None,
            suppress_empty=suppress_empty,
            teams_urls=teams_urls.split(",") if teams_urls else None,
            title=title,
        )


@scm.command("notations")
@click.pass_obj
@pretty_print
def list_notations(controller):
    """List all notations"""
    with Spinner("Fetching notations"):
        return controller.list_notations()


@scm.command("history")
@click.option("--odata_filter", help="OData filter string")
@click.option("--start", help="start date")
@click.option("--end", help="end date")
@click.pass_obj
@pretty_print
def list_history(controller, odata_filter, start, end):
    """List history"""
    with Spinner("Fetching SCM history"):
        return controller.list_history(start, end, filter=odata_filter)


@click.group()
@click.pass_context
def report(ctx):
    """SCM report commands"""
    ctx.obj = ScmController(account=ctx.obj.account)


scm.add_command(report)


@report.command("get")
@click.argument("report_id")
@click.pass_obj
@pretty_print
def get_report(controller, report_id):
    with Spinner("Fetching report"):
        return controller.get_report(report_id)


@report.command("list")
@click.pass_obj
@pretty_print
def list_reports(controller):
    with Spinner("Fetching reports"):
        return controller.list_reports()


@report.command("delete")
@click.argument("report_id")
@click.confirmation_option(prompt="Are you sure?")
@click.pass_obj
@pretty_print
def delete_report(controller, report_id):
    with Spinner("Deleting report"):
        return controller.delete_report(report_id)


@report.command("put")
@click.option(
    "--report_data", help="report data in JSON format, cannot be used with report_file"
)
@click.option(
    "--report_file",
    help="report data JSON file, will ignore report_data if provided",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("--report_id", help="report ID to update")
@click.pass_obj
@pretty_print
def put_report(controller, report_data, report_file, report_id):
    if not report_data and not report_file:
        raise ValueError("Either report_data or report_file must be provided")

    with Spinner("Updating report"):
        if report_file:
            with open(report_file, "r") as f:
                report_data = f.read()
        report_data = json.loads(report_data)
        return controller.put_report(report_data, report_id)


@report.command("chart-data")
@click.argument(
    "scm_category",
    type=click.Choice(
        [c.name for c in SCMCategory if c.value > 0], case_sensitive=False
    ),
)
@click.option("--group_by", "-b", help="field to group by", required=True)
@click.option(
    "--group_limit", "-l", default=100, help="max number of groups to return", type=int
)
@click.option(
    "--sort_by",
    "-s",
    help="sort method",
    type=click.Choice(["count_asc", "count_desc", "group_asc", "group_desc"]),
    default="9-0",
)
@click.option("--display_overrides", "-d", help="display overrides in JSON format")
@click.option(
    "--odata_filter",
    "-f",
    help="OData filter string",
)
@click.option("--scopes", "-c", help="scope-value map in JSON format")
@click.pass_obj
@pretty_print
def get_chart_data(
    controller,
    scm_category,
    group_by,
    group_limit,
    sort_by,
    display_overrides,
    odata_filter,
    scopes,
):
    """Get chart data for SCM reports"""
    display_overrides = json.loads(display_overrides) if display_overrides else None
    scopes = json.loads(scopes) if scopes else None
    with Spinner("Fetching chart data"):
        return controller.get_chart_data(
            scm_category=SCMCategory[scm_category],
            group_by=group_by,
            group_limit=group_limit,
            sort_by=sort_by,
            display_overrides=display_overrides,
            odata_filter=odata_filter,
            scopes=scopes,
        )
