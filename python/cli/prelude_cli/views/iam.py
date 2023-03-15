import click

from rich import print_json
from datetime import datetime, timedelta

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.models.codes import Permission, Mode
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
    creds = controller.new_account(handle=click.prompt('Enter a handle'))
    print_json(data=creds)


@iam.command('update-account')
@click.option('-m', '--mode',
              help='provide a mode',
              default=Mode.MANUAL.name, show_default=True,
              type=click.Choice([m.name for m in Mode], case_sensitive=False))
@click.pass_obj
@handle_api_error
def update_account(controller, mode):
    """ Update an account """
    controller.update_account(mode=Mode[mode.upper()].value)


@iam.command('account')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """ Get account details """
    print_json(data=controller.get_account())


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
    resp = controller.create_user(
        handle=handle, 
        permission=Permission[permission.upper()].value, 
        expires=expires
    )
    print_json(data=resp)


@iam.command('delete-user')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('handle')
@click.pass_obj
@handle_api_error
def delete_user(controller, handle):
    """ Remove a user from your account """
    controller.delete_user(handle=handle)


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


@iam.command('detach-control')
@click.confirmation_option(prompt='Are you sure?')
@click.argument('name')
@click.pass_obj
@handle_api_error
def attach_control(controller, name):
    """ Detach an existing control from your account """
    controller.detach_control(name=name)


@iam.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete your account """
    controller.purge_account()
