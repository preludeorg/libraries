import click


@click.command()
@click.pass_obj
def configure(account):
    """Configure your local keychain"""
    profile = click.prompt(
        "Enter the profile name",
        default=account.profile or "default",
        show_default=True,
    )
    hq = click.prompt("Enter the Prelude API", default=account.hq, show_default=True)
    account_id = click.prompt("Enter your account ID")
    handle = click.prompt("Enter your user handle (email)")
    oidc = click.prompt(
        "If authenticating via OIDC, enter the provider name",
        default="none",
        type=click.Choice(["google", "custom", "none"], case_sensitive=False),
    ).lower()
    slug = None
    if oidc == "none":
        oidc = None
    elif oidc == "custom":
        slug = click.prompt("Please enter your account slug")
    account.keychain.configure_keychain(
        account=account_id, handle=handle, hq=hq, oidc=oidc, profile=profile, slug=slug
    )
    click.secho("Credentials saved", fg="green")
