import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.models.codes import BackgroundJobTypes


@click.group()
@click.pass_context
def jobs(ctx):
    """ Jobs system commands """
    ctx.obj = JobsController(account=ctx.obj)

@jobs.command('background-jobs')
@click.option('-t', '--job_type', help='filter by job type',
              type=click.Choice([t.name for t in BackgroundJobTypes if t != BackgroundJobTypes.INVALID], case_sensitive=False))
@click.option('-l', '--limit', help='limit the number of jobs returned (per job type)', type=int)
@click.pass_obj
@pretty_print
def background_jobs(controller, job_type, limit):
    """ List background jobs """
    with Spinner(description='Fetching background job statuses'):
        result = controller.job_statuses()
        if job_type:
            result = {job_type: result[job_type]}
        if limit:
            result = {k: v[:limit] for k, v in result.items()}
        return result

@jobs.command('background-job')
@click.option('-j', '--job_id', required=True, help='background job ID to retrieve status for')
@click.pass_obj
@pretty_print
def job_status(controller, job_id):
    """ Get status of a given background job """
    with Spinner(description='Fetching background job status'):
        return controller.job_status(job_id=job_id)
