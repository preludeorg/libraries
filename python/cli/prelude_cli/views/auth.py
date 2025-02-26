import click

from prelude_cli.views.shared import Spinner


@click.group()
@click.pass_context
def auth(ctx):
    """Authentication"""
    pass


@auth.command("password")
@click.option("-p", "--password", required=True, type=str)
@click.pass_obj
def login(account, password):
    """Login using your password"""
    with Spinner(description="Logging in and saving tokens"):
        account.password_login(password)
    click.secho("Login successful", fg="green")


@auth.command("refresh")
@click.pass_obj
def refresh(account):
    """Refresh your tokens"""
    with Spinner(description="Refreshing tokens"):
        account.refresh_tokens()
    click.secho("New access tokens saved", fg="green")
