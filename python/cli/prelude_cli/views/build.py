import importlib.resources as pkg_resources
import uuid
from pathlib import Path

import click
import prelude_cli.templates as templates
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.models.codes import Colors
from rich import print_json

from prelude_sdk.controllers.build_controller import BuildController


@click.group()
@click.pass_context
def build(ctx):
    """ Maintain your TTP database """
    ctx.obj = BuildController(account=ctx.obj)


@build.command('list-manifest')
@click.pass_obj
@handle_api_error
def view_manifest(controller):
    """ Print my manifest """
    print_json(data=controller.list_manifest())


@build.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Clone my project locally """
    Path('prelude').mkdir(exist_ok=True)

    listing = controller.list_manifest()
    for ttp in listing:
        for dcf in controller.get_ttp(ttp=ttp):
            with open(f'prelude/{dcf}', 'wb') as code_file:
                code_file.write(controller.clone(name=dcf))
                click.secho(f'Cloned {dcf}')
    click.secho('Project cloned successfully', fg=Colors.GREEN.value)


@build.command('create-ttp')
@click.argument('name')
@click.option('--ttp', help='TTP identifier to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create(controller, ttp, name):
    """ Add a TTP """
    controller.create_ttp(ttp=ttp, name=name)
    click.secho(f'Added {ttp}', fg=Colors.GREEN.value)


@build.command('put-code-file')
@click.argument('path')
@click.pass_obj
@handle_api_error
def add_dcf(controller, path):
    """ Upload a code file """
    with open(path, 'r') as code_file:
        controller.put_code_file(name=Path(path).name, code=code_file.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@build.command('delete-ttp')
@click.argument('ttp')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_ttp(controller, ttp):
    """ Remove a TTP """
    controller.delete_ttp(ttp=ttp)
    click.secho(f'Deleted {ttp}', fg=Colors.GREEN.value)


@build.command('create-code-file')
@click.argument('ttp')
@click.pass_obj
@handle_api_error
def generate_code_file(controller, ttp):
    """ Create a new code file """
    platform = click.prompt(
        text='Enter your desired platform',
        type=click.Choice(['*', 'darwin', 'linux']),
        show_choices=True,
        default='*'
    )
    if platform is not '*':
        ttp = f'{ttp}_{platform}'
        architecture = click.prompt(
            text='Enter your desired architecture',
            type=click.Choice(['*', 'arm64', 'x86_64']),
            show_choices=True,
            default='*'
        )
        if architecture is not '*':
            ttp = f'{ttp}-{architecture}'

    extension = click.prompt(
        text='Enter a file extension',
        type=click.Choice(['c', 'cs', 'swift']),
        show_choices=True
    )
    ttp = f'{ttp}.{extension}'

    filepath = Path(ttp)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open('w') as f:
        f.write(pkg_resources.read_text(templates, f'template.{extension}'))
    click.secho(f'Generated {ttp}', fg=Colors.GREEN.value)
