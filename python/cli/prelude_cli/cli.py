import click
from prelude_cli.views.iam import iam
from prelude_cli.views.configure import configure
from prelude_cli.views.compute import compute
from prelude_cli.views.build import build
from prelude_cli.views.detect import detect
from prelude_sdk.models.account import Account


@click.group()
@click.pass_context
@click.option('--profile', default='default', help='detect keychain profile', show_default=True)
def cli(ctx, profile):
    ctx.obj = Account(profile=profile)


cli.add_command(iam)
cli.add_command(configure)
cli.add_command(detect)
cli.add_command(build)
cli.add_command(compute)


if __name__ == '__main__':
    cli()
