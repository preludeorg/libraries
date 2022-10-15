import uuid
from pathlib import Path

import click
from rich import print_json

from detect_cli.views.shared import handle_api_error
from detect_sdk.controllers.manifest_controller import ManifestController
from detect_sdk.models.codes import Colors


@click.group()
@click.pass_context
def manifest(ctx):
    """ Maintain your TTP database """
    ctx.obj = ManifestController(account=ctx.obj)


@manifest.command('view')
@click.pass_obj
@handle_api_error
def view_manifest(controller):
    """ Print your TTP manifest """
    print_json(data=controller.print_manifest())


@manifest.command('delete-ttp')
@click.argument('ttp')
@click.confirmation_option(prompt='Do you want to delete the TTP?')
@click.pass_obj
@handle_api_error
def delete_ttp(controller, ttp):
    """ Delete a TTP by ID """
    controller.delete_ttp(ttp=ttp)
    click.secho(f'Deleted {ttp}', fg=Colors.GREEN.value)


@manifest.command('add-ttp')
@click.argument('name')
@click.option('--ttp', help='TTP identifier to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def add_ttp(controller, ttp, name):
    """ Upsert a TTP """
    controller.add_ttp(ttp=ttp, name=name)
    click.secho(f'Added {ttp}', fg=Colors.GREEN.value)


@manifest.command('clone')
@click.option('--ttp', help='TTP identifier to clone')
@click.pass_obj
@handle_api_error
def clone(controller, ttp):
    """ Clone code file(s) """
    selection = [ttp] if ttp else controller.print_manifest()
    for ttp_id in selection:
        Path(ttp_id).mkdir(exist_ok=True)
        result = controller.view_ttp(ttp=ttp_id)
        for dcf in result['dcf']:
            with open(f'{ttp_id}/{dcf}', 'wb') as code_file:
                code_file.write(controller.clone_dcf(name=dcf))
                click.secho(f'Cloned {dcf}', fg=Colors.GREEN.value)


@manifest.command('delete-dcf')
@click.argument('name')
@click.confirmation_option(prompt='Do you want to delete the DCF?')
@click.pass_obj
@handle_api_error
def delete_dcf(controller, name):
    """ Delete a code file """
    controller.delete_dcf(name=name)
    click.secho(f'Deleted {name}', fg=Colors.GREEN.value)


@manifest.command('add-dcf')
@click.argument('path')
@click.pass_obj
@handle_api_error
def add_dcf(controller, path):
    """ Upsert a code file """
    with open(path, 'r') as code_file:
        controller.upload_dcf(name=Path(path).name, code=code_file.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)
