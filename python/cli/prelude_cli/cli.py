import click
from prelude_cli.views.iam import iam
from prelude_cli.views.configure import configure
from prelude_cli.views.build import build
from prelude_cli.views.detect import detect
from prelude_sdk.models.account import Account


def complete_profile(ctx, param, incomplete):
    return [x for x in Account().read_keychain_config()]


@click.group()
@click.version_option()
@click.pass_context
@click.option('--profile', default='default', help='The prelude keychain profile to use', show_default=True, shell_complete=complete_profile)
def cli(ctx, profile):
    ctx.obj = Account(profile=profile)


cli.add_command(iam)
cli.add_command(configure)
cli.add_command(detect)
cli.add_command(build)


if __name__ == '__main__':
    cli()
