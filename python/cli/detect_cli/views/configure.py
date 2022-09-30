import click

from detect_sdk.models.codes import Colors


@click.command()
@click.pass_obj
def configure(account):
    """Configure your Detect credentials"""
    profile = click.prompt('Enter the profile name', default=account.profile, show_default=True)
    hq = click.prompt('Enter the Detect URL', default=account.hq, show_default=True)
    account_id = click.prompt('Enter your account ID')
    account_token = click.prompt('Enter your account token')
    account.configure(account_id=account_id, token=account_token, hq=hq, profile=profile)
    click.secho('Credentials configured!', fg=Colors.GREEN.value)
