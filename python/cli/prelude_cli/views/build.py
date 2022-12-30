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
    """ Terminal-based security test environment """
    ctx.obj = BuildController(account=ctx.obj)


@build.command('clone')
@click.pass_obj
@handle_api_error
def clone(controller):
    """ Download all tests to your local environment """
    Path('prelude').mkdir(exist_ok=True)
    for test in controller.list_tests():
        code = controller.download_test(ident=test['id'])
        with open(f'prelude/{test["id"]}.go', 'wb') as test_code:
            test_code.write(code)
            click.secho(f'Cloned {test["id"]}')
    click.secho('Project cloned successfully', fg=Colors.GREEN.value)


@build.command('download')
@click.pass_obj
@click.argument('test')
@handle_api_error
def download(controller, test):
    """ Download a single test to your local environment """
    code = controller.download_test(ident=test)
    with open(f'{test["id"]}.go', 'wb') as test_code:
        test_code.write(code)
        click.secho(f'Cloned {test["id"]}')


@build.command('list-tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ List all tests """
    print_json(data=controller.list_tests())


@build.command('create-test')
@click.argument('question')
@click.pass_obj
@handle_api_error
def create_test(controller, test, question):
    """ Create a new test """
    controller.create_test(ident=test, question=question)
    template = pkg_resources.read_text(templates, 'template.go')
    controller.upload_test(name=f'{test}.go', code=template)
    click.secho(f'Added {test}', fg=Colors.GREEN.value)


@build.command('delete-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test):
    """ Delete TEST """
    controller.delete_test(ident=test)
    click.secho(f'Deleted {test}', fg=Colors.GREEN.value)


@build.command('list-vst')
@click.pass_obj
@handle_api_error
def list_vst(controller):
    """ List all verified tests """
    print_json(data=controller.list_vst())


@build.command('delete-vst')
@click.argument('vst')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_vst(controller, variant):
    """ Delete VST

    VST is the full name of a verified test
    """
    controller.delete_vst(name=variant)
    click.secho(f'Deleted {variant}', fg=Colors.GREEN.value)


@build.command('save')
@click.argument('path', type=click.Path(exists=True))
@click.pass_obj
@handle_api_error
def save_test(controller, path):
    """ Upload the test at PATH """
    with open(path, 'r') as variant:
        controller.upload_test(name=Path(path).name, code=variant.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@build.command('url')
@click.argument('vst')
@click.pass_obj
@handle_api_error
def create_url(controller, name):
    """ Generate a download URL for VST

    NAME is the name of a _verified_ test
    """
    print_json(data=controller.create_url(name=name))


@build.command('compute')
@click.argument('test')
@click.pass_obj
@handle_api_error
def compute(controller, test):
    """ Compile and validate a TEST """
    print_json(data=controller.compute(name=test))
