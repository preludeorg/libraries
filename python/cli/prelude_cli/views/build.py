import importlib.resources as pkg_resources
import uuid
import re

from datetime import datetime
from pathlib import Path, PurePath

import click
import prelude_cli.templates as templates
from prelude_cli.views.shared import handle_api_error
from prelude_sdk.models.codes import Colors
from rich import print_json

from prelude_sdk.controllers.build_controller import BuildController


UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


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
    for test in controller.list_tests():
        click.secho(f'Cloning {test["id"]}')
        my_test = PurePath('prelude', test['id'])
        Path(my_test).mkdir(parents=True, exist_ok=True)

        for attach in controller.attachments(test_id=test['id']):
            if Path(attach).suffix:
                code = controller.download(test_id=test['id'], filename=attach)
                with open(PurePath(my_test, attach), 'wb') as f:
                    f.write(code)
    click.secho('Project cloned successfully', fg=Colors.GREEN.value)

@build.command('list-tests')
@click.pass_obj
@handle_api_error
def list_tests(controller):
    """ List all security tests """
    print_json(data=controller.list_tests())


@build.command('attachments')
@click.argument('test_id')
@click.pass_obj
@handle_api_error
def list_attachments(controller, test_id):
    """ List attachments for a test """
    print_json(data=controller.attachments(test_id=test_id))


@build.command('create-test')
@click.argument('rule')
@click.pass_obj
@handle_api_error
def create_test(controller, rule):
    """ Create a new security test """
    test_id = str(uuid.uuid4())
    basename = f'{test_id}.go'

    controller.create_test(test_id=test_id, rule=rule)
    template = pkg_resources.read_text(templates, 'template.go')
    template = template.replace('$ID', test_id)
    template = template.replace('$RULE', rule)
    template = template.replace('$CREATED', str(datetime.now()))
    controller.upload(test_id=test_id, filename=basename, code=template)

    with open(basename, 'w') as test_code:
        test_code.write(template)
        click.secho(f'Created {basename}', fg=Colors.GREEN.value)


@build.command('delete-test')
@click.argument('test_id')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test_id):
    """ Delete TEST """
    controller.delete_test(test_id=test_id)
    click.secho(f'Deleted {test_id}', fg=Colors.GREEN.value)


@build.command('upload')
@click.argument('path', type=click.Path(exists=True))
@click.option('--test', help='test identifier for this attachment', default=None, type=str)
@click.pass_obj
@handle_api_error
def upload_attachment(controller, path, test):
    """ Upload a security test or test attachment from disk """
    def test_id():
        match = UUID.search(path)
        if match:
            return match.group(0)
        raise FileNotFoundError('Must specify a test ID or include it in the filename')

    with open(path, 'r') as source_code:
        controller.upload(test_id=test or test_id(), filename=Path(path).name, code=source_code.read())
        click.secho(f'Uploaded {path}', fg=Colors.GREEN.value)


@build.command('url')
@click.argument('attachment')
@click.pass_obj
@handle_api_error
def create_url(controller, attachment):
    """ Generate a download URL from an attachment """
    print_json(data=controller.create_url(attachment=attachment))


@build.command('compute')
@click.argument('test')
@click.pass_obj
@handle_api_error
def compute(controller, test):
    """ Create a VST from a test """
    print_json(data=controller.compute(test_id=test))
