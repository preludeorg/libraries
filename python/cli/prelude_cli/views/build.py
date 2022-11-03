import importlib.resources as pkg_resources
import pathlib
import uuid
from datetime import datetime
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
            with open(f'prelude/{dcf}', 'wb') as test:
                test.write(controller.clone(name=dcf))
                click.secho(f'Cloned {dcf}')
    click.secho('Project cloned successfully', fg=Colors.GREEN.value)


@build.command('put-ttp')
@click.argument('question')
@click.option('--ttp', help='TTP identifier to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create(controller, ttp, question):
    """ Add a TTP """
    controller.create_ttp(ttp=ttp, question=question)
    click.secho(f'Added {ttp}', fg=Colors.GREEN.value)


@build.command('put-test')
@click.argument('path')
@click.pass_obj
@handle_api_error
def add_test(controller, path):
    """ Upload a test """
    with open(path, 'r') as test:
        controller.put_test(name=Path(path).name, code=test.read())
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


@build.command('delete-test')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, name):
    """ Remove a test """
    controller.delete_test(name=name)
    click.secho(f'Deleted {name}', fg=Colors.GREEN.value)


@build.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete all stored TTPs and tests """
    controller.delete_manifest()
    click.secho('Storage has been purged', fg=Colors.GREEN.value)


@build.command('purge-compiled')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge_compiled_tests(controller):
    """ Delete all compiled tests """
    text = controller.delete_compiled_tests()
    click.secho(text, fg=Colors.GREEN.value)


@build.command('create-test')
@click.option('--ttp', help='TTP identifier', default=str(uuid.uuid4()))
@click.option('--path', help='directory to store code file', default='.')
@click.pass_obj
@handle_api_error
def generate_test(controller, ttp, path):
    """ Create a new test """
    def platform():
        p = click.prompt(
            text='Select a platform',
            type=click.Choice(['*', 'darwin', 'linux']),
            show_choices=True,
            default='*'
        )
        return p if p is not '*' else None

    def architecture():
        a = click.prompt(
            text='Select an architecture',
            type=click.Choice(['*', 'arm64', 'x86_64']),
            show_choices=True,
            default='*'
        )
        return a if a is not '*' else None

    def extension():
        return click.prompt(
            text='Select a language',
            type=click.Choice(['c', 'cs', 'swift']),
            show_choices=True
        )

    # get TTP to work with
    question = controller.list_manifest().get(ttp)
    if not question:
        question = click.prompt('No TTP supplied. Ask a question to create a new TTP: ')
        controller.create_ttp(ttp=ttp, question=question)

    # generate a name
    code_name = ttp
    platform = platform()
    if platform:
        code_name = f'{code_name}_{platform}'
        arch = architecture()
        if arch:
            code_name = f'{code_name}-{arch}'
    ext = extension()
    code_name = f'{code_name}.{ext}'

    # create test
    filepath = Path(pathlib.PurePath(path, code_name))
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open('w') as f:
        template = pkg_resources.read_text(templates, f'template.{ext}')
        template = template.replace('$NAME', code_name)
        template = template.replace('$QUESTION', question)
        template = template.replace('$CREATED', str(datetime.now()))
        f.write(template)
    click.secho(f'Generated {code_name}', fg=Colors.GREEN.value)
    controller.put_test(name=code_name, code=template, create=True)
