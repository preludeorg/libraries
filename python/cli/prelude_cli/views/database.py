import uuid
from pathlib import Path, PurePath

import click
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.database_controller import DatabaseController
from prelude_sdk.models.codes import Colors
from rich import print_json


@click.group()
@click.pass_context
def database(ctx):
    """ Maintain your TTP database """
    ctx.obj = DatabaseController(account=ctx.obj)


@database.command('view')
@click.pass_obj
@handle_api_error
def view_manifest(controller):
    """ Print my manifest """
    print_json(data=controller.print_manifest())


@database.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Clone my project locally """
    home = Path(PurePath(Path.home(), '.prelude', 'src'))
    home.mkdir(exist_ok=True)

    listing = controller.print_manifest()
    for ttp in listing:
        for dcf in controller.view_ttp(ttp=ttp):
            with open(f'{home}/{dcf}', 'wb') as code_file:
                code_file.write(controller.clone(name=dcf))
                click.secho(f'Cloned {dcf}')
    click.secho(f'Project cloned to {home}', fg=Colors.GREEN.value)


@database.command('create')
@click.argument('name')
@click.option('--ttp', help='TTP identifier to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create(controller, ttp, name):
    """ Add or update a TTP """
    controller.add_ttp(ttp=ttp, name=name)
    click.secho(f'Added {ttp}', fg=Colors.GREEN.value)


@database.command('upload')
@click.argument('path')
@click.pass_obj
@handle_api_error
def add_dcf(controller, path):
    """ Upload a code file """
    with open(path, 'r') as code_file:
        controller.upload_dcf(name=Path(path).name, code=code_file.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@database.command('delete')
@click.argument('ttp')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_ttp(controller, ttp):
    """ Remove a TTP """
    controller.delete_ttp(ttp=ttp)
    click.secho(f'Deleted {ttp}', fg=Colors.GREEN.value)
