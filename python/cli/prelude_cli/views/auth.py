import click

from prelude_cli.views.shared import Spinner, pretty_print


@click.group()
@click.pass_context
def auth(ctx):
    """Authentication"""
    pass


@auth.command("login")
@click.option("-p", "--password", prompt=True, hide_input=True, required=True)
@click.pass_obj
@pretty_print
def login(account, password):
    """Login using your password"""
    with Spinner(description="Logging in and saving tokens"):
        return account.password_login(password), "Login successful"


@auth.command("refresh")
@click.pass_obj
@pretty_print
def refresh(account):
    """Refresh your tokens"""
    with Spinner(description="Refreshing tokens"):
        return account.refresh_tokens(), "New access tokens saved"
