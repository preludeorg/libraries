import click
from detect_cli.views.account import account
from detect_cli.views.configure import configure
from detect_cli.views.database import database
from detect_cli.views.detect import detect
from detect_sdk.models.account import Account


@click.group()
@click.pass_context
@click.option('--profile', default='default', help='detect keychain profile', show_default=True)
def cli(ctx, profile):
    ctx.obj = Account(profile=profile)


cli.add_command(account)
cli.add_command(configure)
cli.add_command(detect)
cli.add_command(database)


if __name__ == '__main__':
    cli()
