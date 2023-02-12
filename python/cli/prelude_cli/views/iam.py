import click

from rich import print_json

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import Permission


@click.group()
@click.pass_context
def iam(ctx):
    """ Administer your account """
    ctx.obj = IAMController(account=ctx.obj)


@iam.command('create-account')
@click.pass_obj
@handle_api_error
@click.confirmation_option(prompt='Overwrite local account credentials for selected profile?')
def register_account(controller):
    """ Register a new account """
    creds = controller.new_account(handle=click.prompt('Enter a handle'))
    print_json(data=creds)
    click.secho('Your keychain has been updated to use this account', fg='green')


@iam.command('account')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """ Get account details """
    acct = controller.get_account()
    users = {user["handle"]: Permission(user["permission"]).name for user in acct['users']}
    print_json(data=dict(whoami=acct['whoami'], users=users, controls=acct['controls']))


@iam.command('create-user')
@click.option('-p', '--permission', help='provide a permission level', default=[p.name for p in Permission][-1],
              type=click.Choice([p.name for p in Permission], case_sensitive=False), show_default=True)
@click.argument('handle')
@click.pass_obj
@handle_api_error
def create_user(controller, permission, handle):
    """ Create a new user in your account """
    token = controller.create_user(handle=handle, permission=Permission[permission.upper()].value)
    click.secho(f'Created new [{permission}] user [{handle}]. Token: {token}', fg='green')


@iam.command('delete-user')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('handle')
@click.pass_obj
@handle_api_error
def delete_user(controller, handle):
    """ Remove a user from your account """
    if controller.delete_user(handle=handle):
        click.secho(f'Deleted user {handle}', fg='green')


@iam.command('attach-control')
@click.argument('name')
@click.option('--api', required=True, help='API endpoint of the control')
@click.option('--user', required=True, help='user identifier')
@click.option('--secret', default='', help='secret for OAUTH use cases')
@click.pass_obj
@handle_api_error
def attach_control(controller, name, api, user, secret):
    """ Attach an EDR or SIEM to Detect """
    controller.attach_control(name=name, api=api, user=user, secret=secret)
    click.secho(f'Attached "{name}" to your Detect account', fg='green')


@iam.command('detach-control')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('name')
@click.pass_obj
@handle_api_error
def attach_control(controller, name):
    """ Detach an existing control from your account """
    controller.detach_control(name=name)
    click.secho(f'Detached "{name}" from your Detect account', fg='red')


@iam.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete your account """
    controller.purge_account()
    click.secho('Your account has been deleted', fg='green')
