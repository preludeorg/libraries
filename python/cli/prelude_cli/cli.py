import click

from prelude_cli.views.iam import iam
from prelude_cli.views.build import build
from prelude_cli.views.detect import detect
from prelude_sdk.models.account import Account
from prelude_cli.views.configure import configure
from prelude_cli.views.interactive import interactive as interactive_command


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
@click.option('--profile', default='default', help='The prelude keychain profile to use', show_default=True)
@click.option('--interactive', help='Open interactive wizard (cannot be used with a subcommand)', default=False, is_flag=True)
def cli(ctx, profile, interactive):
    ctx.obj = Account(profile=profile)
    if ctx.invoked_subcommand is None:
        if interactive:
            ctx.invoke(interactive_command)
        else:
            click.echo(ctx.get_help())


cli.add_command(iam)
cli.add_command(configure)
cli.add_command(detect)
cli.add_command(build)


if __name__ == '__main__':
    cli()
