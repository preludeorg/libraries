import click
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import Colors, Permission
from rich import print_json


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
    click.secho('Your keychain has been updated to use this account', fg=Colors.GREEN.value)


@iam.command('list-users')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """ List all users in your account """
    users = {user["handle"]: Permission(user["permission"]).name for user in controller.get_users()}
    print_json(data=users)


@iam.command('create-user')
@click.option('--permission', help='provide a permission level', default=[p.name for p in Permission][-1],
              type=click.Choice([p.name for p in Permission], case_sensitive=False), show_default=True)
@click.argument('handle')
@click.pass_obj
@handle_api_error
def create_user(controller, permission, handle):
    """ Create a new user in your account """
    token = controller.create_user(handle=handle, permission=Permission[permission.upper()].value)
    click.secho(f'Created new [{permission}] user [{handle}]. Token: {token}', fg=Colors.GREEN.value)


@iam.command('delete-user')
@click.argument('handle')
@click.pass_obj
@handle_api_error
def delete_user(controller, handle):
    """ Remove a user from your account """
    if controller.delete_user(handle=handle):
        click.secho(f'Deleted user {handle}', fg=Colors.GREEN.value)


@iam.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete your account """
    controller.purge_account()
    click.secho('Your account has been deleted', fg=Colors.GREEN.value)
