import click
import webbrowser

from prelude_cli.views.shared import Spinner, pretty_print


@click.group()
@click.pass_context
def auth(ctx):
    """Authentication"""
    pass


@auth.command("login")
@click.option("-p", "--password", type=str, help="password for login")
@click.pass_obj
@pretty_print
def login(account, password):
    """Login using password or SSO"""
    if not account.oidc:
        password = password or click.prompt("Password", type=str, hide_input=True)
        with Spinner(description="Logging in and saving tokens"):
            return account.password_login(password), "Login with password successful"

    url = f"{account.hq.replace('api', 'platform')}/cli-auth?handle={account.handle}&provider={account.oidc}"
    if account.oidc == "custom":
        slug = account.slug or click.prompt("Please enter your account slug")
        url += f"&slug={slug}"
    webbrowser.open(url)
    code = click.prompt(
        f"Launching browser for authentication:\n\n{url}\n\nPlease enter your authorization code here"
    )
    verifier, authorization_code = code.split("/")
    with Spinner(description="Logging in and saving tokens"):
        tokens = account.exchange_authorization_code(
            authorization_code, verifier, source="cli"
        )
    return tokens, "Login with SSO successful"


@auth.command("refresh")
@click.pass_obj
@pretty_print
def refresh(account):
    """Refresh your tokens"""
    with Spinner(description="Refreshing tokens"):
        return account.refresh_tokens(), "New access tokens saved"
