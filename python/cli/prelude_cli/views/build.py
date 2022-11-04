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
    """ A terminal-based IDE """
    ctx.obj = BuildController(account=ctx.obj)


@build.command('purge')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def purge(controller):
    """ Delete all stored tests and variants """
    controller.purge_account()
    click.secho('Storage has been purged', fg=Colors.GREEN.value)


@build.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Clone my project locally """
    Path('prelude').mkdir(exist_ok=True)
    for test in controller.list_tests():
        for variant in controller.get_test(ident=test['id']):
            with open(f'prelude/{variant}', 'wb') as code:
                code.write(controller.clone(name=variant))
                click.secho(f'Cloned {variant}')
    click.secho('Project cloned successfully', fg=Colors.GREEN.value)


@build.command('list-tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ Display my tests """
    print_json(data=controller.list_tests())


@build.command('create-test')
@click.argument('question')
@click.option('--test', help='Test ID to update', default=str(uuid.uuid4()))
@click.pass_obj
@handle_api_error
def create_test(controller, test, question):
    """ Add a test """
    controller.create_test(ident=test, question=question)
    click.secho(f'Added {test}', fg=Colors.GREEN.value)


@build.command('delete-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test):
    """ Remove a test """
    controller.delete_test(ident=test)
    click.secho(f'Deleted {test}', fg=Colors.GREEN.value)


@build.command('delete-variant')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_variant(controller, name):
    """ Remove a variant """
    controller.delete_variant(name=name)
    click.secho(f'Deleted {name}', fg=Colors.GREEN.value)


@build.command('save-variant')
@click.argument('path')
@click.pass_obj
@handle_api_error
def put_variant(controller, path):
    """ Save a variant """
    with open(path, 'r') as variant:
        controller.create_variant(name=Path(path).name, code=variant.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@build.command('create-variant')
@click.option('--test', help='Test ID', default=str(uuid.uuid4()))
@click.option('--path', help='directory to store code file', default='.')
@click.pass_obj
@handle_api_error
def generate_test(controller, test, path):
    """ Create a new test variant """
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

    # get test to work with
    tests = controller.list_tests()
    question = next((t.get('question') for t in tests if t['id'] == test), None)
    if not question:
        question = click.prompt('No test supplied. Ask a question to create a new test: ')
        controller.create_test(ident=test, question=question)

    # generate a name
    code_name = test
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
    controller.create_variant(name=code_name, code=template)
