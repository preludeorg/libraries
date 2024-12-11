import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.jobs_controller import JobsController


@click.group()
@click.pass_context
def jobs(ctx):
    """ Jobs system commands """
    ctx.obj = JobsController(account=ctx.obj)

@jobs.command('statuses')
@click.pass_obj
@pretty_print
def job_statuses(controller):
    """ Get statuses of background jobs """
    with Spinner(description='Getting background job statuses'):
        return controller.job_statuses()

@jobs.command('status')
@click.option('-j', '--job_id', required=True, help='background job ID to retrieve status for')
@click.pass_obj
@pretty_print
def job_status(controller, job_id):
    """ Get status of a given background job """
    with Spinner(description='Getting background job status'):
        return controller.job_status(job_id=job_id)
