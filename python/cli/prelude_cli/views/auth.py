import click

from prelude_cli.views.shared import Spinner, pretty_print
from prelude_cli.views.sso import (
    authorize_with_flask,
    exchange_for_tokens,
    get_auth_url,
    OIDC_REDIRECT_URI,
)


@click.group()
@click.pass_context
def auth(ctx):
    """Authentication"""
    pass


@auth.command("login")
@click.option(
    "-p", "--password", type=str, help="password for login. Ignored if SSO is used"
)
@click.option("--sso", is_flag=True, default=False, help="use SSO for login")
@click.option(
    "--local_server",
    is_flag=True,
    default=False,
    help="use local Flask server to catch SSO callback automatically",
)
@click.pass_obj
@pretty_print
def login(account, password, sso, local_server):
    """Login using password or SSO"""
    if not sso:
        password = password or click.prompt("Password", type=str, hide_input=True)
        with Spinner(description="Logging in and saving tokens"):
            return account.password_login(password), "Login with password successful"
    if local_server:
        with Spinner(description="Launching browser for authentication..."):
            tokens = authorize_with_flask()
    else:
        auth_url = get_auth_url(OIDC_REDIRECT_URI)
        authorization_code = click.prompt(
            f"Please open:\n{auth_url}\nin your browser and authenticate. Enter the authorization code you received"
        )
        tokens = exchange_for_tokens(authorization_code, OIDC_REDIRECT_URI)
    account.save_new_token(tokens)
    return tokens, "Login with SSO successful"


@auth.command("refresh")
@click.pass_obj
@pretty_print
def refresh(account):
    """Refresh your tokens"""
    with Spinner(description="Refreshing tokens"):
        return account.refresh_tokens(), "New access tokens saved"
