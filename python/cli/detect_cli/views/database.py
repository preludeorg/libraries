import json
import uuid
from pathlib import Path, PurePath

import click
from detect_cli.views.shared import handle_api_error
from detect_sdk.models.codes import Colors
from detect_sdk.controllers.database_controller import DatabaseController
from rich import print_json


@click.group()
@click.pass_context
def database(ctx):
    """ Manage your TTP database """
    ctx.obj = DatabaseController(account=ctx.obj)


@database.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Clone my project """
    home = Path(PurePath(Path.home(), '.prelude', 'src'))
    home.mkdir(exist_ok=True)

    listing = controller.print_manifest()
    for ttp in listing:
        result = controller.view_ttp(ttp=ttp)
        for dcf in result['dcf']:
            with open(f'{home}/{dcf}', 'wb') as code_file:
                code_file.write(controller.clone(name=dcf))
                click.secho(f'Cloned {dcf}')
    mani = Path(PurePath(Path.home(), '.prelude'))
    with open(f'{mani}/manifest.json', 'w') as m:
        m.write(json.dumps(listing))
        click.secho(f'Cloned manifest.json')
    click.secho(f'Project cloned to {home}', fg=Colors.GREEN.value)


@database.command('add-ttp')
@click.argument('name')
@click.option('--ttp', help='TTP identifier to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create(controller, ttp, name):
    """ Upsert a TTP """
    controller.add_ttp(ttp=ttp, name=name)
    click.secho(f'Added {ttp}', fg=Colors.GREEN.value)


@database.command('add-dcf')
@click.argument('path')
@click.pass_obj
@handle_api_error
def add_dcf(controller, path):
    """ Upload a code file """
    with open(path, 'r') as code_file:
        controller.upload_dcf(name=Path(path).name, code=code_file.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@database.command('rm-ttp')
@click.argument('ttp')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_ttp(controller, ttp):
    """ Delete a TTP """
    controller.delete_ttp(ttp=ttp)
    click.secho(f'Deleted {ttp}', fg=Colors.GREEN.value)


@database.command('compile')
@click.argument('ttp')
@click.pass_obj
@handle_api_error
def compile_ttp(controller, ttp):
    """ Compile code files """
    for output in controller.compile(ttp=ttp):
        click.secho(f'Compiled: {output}', fg=Colors.GREEN.value)


@database.command('deploy')
@click.argument('ttp')
@click.pass_obj
@handle_api_error
def deploy_ttp(controller, ttp):
    """ Generate download URLs """
    print_json(data=controller.deploy_command(ttp=ttp))
    click.secho('You have 60 seconds to use these URLs', fg=Colors.RED.value)


@database.command('rm-dcf')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_dcf(controller, name):
    """ Delete a code file """
    controller.delete_dcf(name=name)
    click.secho(f'Deleted {name}', fg=Colors.GREEN.value)


@database.command('view')
@click.pass_obj
@handle_api_error
def view_manifest(controller):
    """ Print my manifest """
    print_json(data=controller.print_manifest())
