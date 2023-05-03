import click

from rich import print_json
from datetime import datetime, timedelta

from prelude_sdk.models.codes import Permission, Mode
from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.iam_controller import IAMController


@click.group()
@click.pass_context
def iam(ctx):
    """ Prelude account management """
    ctx.obj = IAMController(account=ctx.obj)


@iam.command('create-account')
@click.pass_obj
@handle_api_error
@click.confirmation_option(prompt='Overwrite local account credentials for selected profile?')
def register_account(controller):
    """ Register a new account """
    handle = click.prompt('Enter a handle')
    with Spinner():
        data = controller.new_account(handle=handle)
    print_json(data=data)
    print("\nCheck your email to verify your account.\n")


@iam.command('update-account')
@click.option('-m', '--mode',
              help='provide a mode',
              default=Mode.MANUAL.name, show_default=True,
              type=click.Choice([m.name for m in Mode], case_sensitive=False))
@click.pass_obj
@handle_api_error
def update_account(controller, mode):
    """ Update an account """
    with Spinner():
        controller.update_account(mode=Mode[mode.upper()].value)


@iam.command('account')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """ Get account details """
    with Spinner():
        data = controller.get_account()
    print_json(data=data)


@iam.command('create-user')
@click.option('-d', '--days', help='days this account should remain active', default=365, type=int)
@click.option('-p', '--permission', help='provide a permission level', default=Permission.SERVICE.name,
              type=click.Choice([p.name for p in Permission], case_sensitive=False), show_default=True)
@click.argument('handle')
@click.pass_obj
@handle_api_error
def create_user(controller, permission, handle, days):
    """ Create a new user in your account """
    expires = datetime.utcnow() + timedelta(days=days)
    with Spinner():
        data = controller.create_user(
            handle=handle,
            permission=Permission[permission.upper()].value,
            expires=expires
        )
    print_json(data=data)
    if permission != Permission.SERVICE.name:
        print("\nCheck your email to verify your account.\n")

@iam.command('delete-user')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('handle')
@click.pass_obj
@handle_api_error
def delete_user(controller, handle):
    """ Remove a user from your account """
    with Spinner():
        controller.delete_user(handle=handle)


@iam.command('logs')
@click.option('-d', '--days', help='days back to search from today', default=7, type=int)
@click.option('-l', '--limit', help='limit the number of results', default=1000, type=int)
@click.pass_obj
@handle_api_error
def logs(controller, days, limit):
    """ Get audit logs """
    with Spinner():
        data = controller.audit_logs(days=days, limit=limit)
    print_json(data=data)


@iam.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete your account """
    with Spinner():
        controller.purge_account()
