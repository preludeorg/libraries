import click


@click.command()
@click.pass_obj
def configure(ctx):
    """ Configure your local keychain """
    profile = click.prompt('Enter the profile name', default=ctx['profile'].profile, show_default=True)
    hq = click.prompt('Enter the Prelude API', default=ctx['profile'].hq, show_default=True)
    account_id = click.prompt('Enter your account ID')
    account_token = click.prompt('Enter your account token')
    ctx['profile'].configure(account_id=account_id, token=account_token, hq=hq, profile=profile)
    click.secho('Credentials saved', fg='green')
