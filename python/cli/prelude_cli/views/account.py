import uuid

import click
from rich import print_json

from detect_sdk.controllers.account_controller import AccountController
from detect_sdk.models.codes import Colors, Permission
from detect_cli.views.shared import handle_api_error


@click.group()
@click.pass_context
def account(ctx):
    """ Administer your account """
    ctx.obj = AccountController(account=ctx.obj)


@account.command('create-user')
@click.option('--permission', help='provide a permission level', default=[p.name for p in Permission][-1],
              type=click.Choice([p.name for p in Permission], case_sensitive=False), show_default=True)
@click.option('--email', help='provide a unique identifier', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create_user(controller, permission, email):
    """Create a new user in the account"""
    token = controller.create_user(email=email, permission=Permission[permission.upper()].value)
    click.secho(f'Created new [{permission}] account [{email}]. Token: {token}', fg=Colors.GREEN.value)


@account.command('delete-user')
@click.argument('email')
@click.pass_obj
@handle_api_error
def delete_user(controller, email):
    """Delete a user from the account"""
    if controller.delete_user(email=email):
        click.secho(f'Deleted user {email}', fg=Colors.GREEN.value)


@account.command('describe')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """View account information"""
    print_json(data=controller.describe_account())


@account.command('token')
@click.confirmation_option(prompt='Do you want to update the account token?')
@click.argument('token')
@click.pass_context
@handle_api_error
def update_token(ctx, token):
    """ Update your account token """
    ctx.obj.update_token(token=token)
    click.secho('Updated account token', fg=Colors.GREEN.value)
    ctx.invoke(describe_account)


@account.command('activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days):
    """ Get a summary of Account activity """
    activity = controller.describe_activity(days=days)
    print_json(data=activity)


@account.command('register')
@click.pass_obj
@handle_api_error
def register_account(controller):
    """ Register a new account """
    creds = controller.new_registration(email=click.prompt('Enter an email'))
    print_json(data=creds)
    click.secho('Configure your keychain to use this account', fg=Colors.GREEN.value)
