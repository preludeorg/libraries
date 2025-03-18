import click

from prelude_cli.views.shared import Spinner, pretty_print


@click.group()
@click.pass_context
def auth(ctx):
    """Authentication"""
    pass


@auth.command("login")
@click.option(
    "-p", "--password", type=str, help="password for login. Ignored if SSO is used"
)
@click.pass_obj
@pretty_print
def login(account, password):
    """Login using password or SSO"""
    if not account.oidc:
        password = password or click.prompt("Password", type=str, hide_input=True)
        with Spinner(description="Logging in and saving tokens"):
            return account.password_login(password), "Login with password successful"

    def _signin_url(platform_url, handle, provider, slug):
        url = f"{platform_url}/cli-auth?handle={handle}&provider={provider}"
        if provider == "custom":
            slug = slug or click.prompt("Please enter your account slug")
            url += f"&slug={slug}"
        return url

    url = _signin_url(
        account.hq.replace("api", "platform"),
        account.handle,
        account.oidc,
        account.slug,
    )
    authorization_code = click.prompt(
        f"Please open the following URL in your browser and authenticate:\n\n{url}\n\nEnter the authorization code here"
    )
    tokens = account.exchange_authorization_code(authorization_code)
    return tokens, "Login with SSO successful"


@auth.command("refresh")
@click.pass_obj
@pretty_print
def refresh(account):
    """Refresh your tokens"""
    with Spinner(description="Refreshing tokens"):
        return account.refresh_tokens(), "New access tokens saved"
