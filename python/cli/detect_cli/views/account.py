import click
import uuid
from rich import print_json

from detect_sdk.controllers.account_controller import AccountController
from detect_sdk.models.codes import Colors, Permission
from detect_cli.views.shared import handle_api_error


@click.group()
@click.pass_context
def account(ctx):
    """Interact with your Account"""
    ctx.obj = AccountController(account=ctx.obj)


@account.command('create-user')
@click.option('--permission', help='provide a permission level', default=[p.name for p in Permission][-1],
              type=click.Choice([p.name for p in Permission], case_sensitive=False), show_default=True)
@click.option('--label', help='provide a unique identifier')
@click.pass_obj
@handle_api_error
def create_user(controller, permission, label):
    """Create a new user in the account"""
    label = label if label else str(uuid.uuid4())
    token = controller.create_user(label=label, permission=Permission[permission.upper()].value)
    click.secho(f'Created new [{permission}] account [{label}]. Token: {token}', fg=Colors.GREEN.value)


@account.command('delete-user')
@click.argument('label')
@click.pass_obj
@handle_api_error
def delete_user(controller, label):
    """Delete a user from the account"""
    if controller.delete_user(label=label):
        click.secho(f'Deleted user {label}', fg=Colors.GREEN.value)


@account.command('describe-account')
@click.pass_obj
@handle_api_error
def describe_account(controller):
    """View account information"""
    print_json(data=controller.describe_account())


@account.command('put-token')
@click.confirmation_option(prompt='Do you want to update the account token?')
@click.argument('token')
@click.pass_context
@handle_api_error
def update_token(ctx, token):
    """Update your account token"""
    ctx.obj.update_token(token=token)
    click.secho('Updated account token', fg=Colors.GREEN.value)
    ctx.invoke(describe_account)


@account.command('describe-activity')
@click.option('--days', help='number of days to search back', default=7, type=int)
@click.pass_obj
@handle_api_error
def describe_activity(controller, days):
    """ Get a summary of Account activity """
    activity = controller.describe_activity(days=days)
    print_json(data=activity)
