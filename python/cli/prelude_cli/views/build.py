import re
import uuid
import click
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from rich import print_json
from datetime import datetime
from pathlib import Path, PurePath

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.build_controller import BuildController


UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


@click.group()
@click.pass_context
def build(ctx):
    """ Custom security tests """
    ctx.obj = BuildController(account=ctx.obj)


@build.command('test')
@click.argument('test_id')
@click.pass_obj
@handle_api_error
def get_test(controller, test_id):
    """ List properties for a test """
    print_json(data=controller.get_test(test_id=test_id))


@build.command('create-test')
@click.argument('name')
@click.option('-t', '--test', help='test identifier', default=None, type=str)
@click.pass_obj
@handle_api_error
def create_test(controller, name, test):
    """ Create or update a security test """
    test_id = test or str(uuid.uuid4())
    controller.create_test(test_id=test_id, name=name)

    if not test:
        basename = f'{test_id}.go'
        template = pkg_resources.read_text(templates, 'template.go')
        template = template.replace('$ID', test_id)
        template = template.replace('$NAME', name)
        template = template.replace('$CREATED', str(datetime.utcnow()))
        controller.upload(test_id=test_id, filename=basename, data=template)

        with open(basename, 'w') as test_code:
            test_code.write(template)
            click.secho(f'Created {basename}', fg='green')


@build.command('delete-test')
@click.argument('test')
@click.option('-t', '--test', help='test identifier', default=None, type=str)
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test):
    """ Delete a test """
    controller.delete_test(test_id=test)
    click.secho(f'Deleted {test}', fg='green')


@build.command('download')
@click.argument('test')
@click.pass_obj
@handle_api_error
def download(controller, test):
    """ Download a test to your local environment """
    click.secho(f'Downloading {test}')
    Path(test).mkdir(parents=True, exist_ok=True)

    for attach in controller.get_test(test_id=test).get('attachments'):
        if Path(attach).suffix:
            code = controller.download(test_id=test, filename=attach)
            with open(PurePath(test, attach), 'wb') as f:
                f.write(code)


@build.command('upload')
@click.argument('path', type=click.Path(exists=True))
@click.option('-t', '--test', help='test identifier', default=None, type=str)
@click.pass_obj
@handle_api_error
def upload_attachment(controller, path, test):
    """ Upload a test attachment from disk """
    def test_id():
        match = UUID.search(path)
        if match:
            return match.group(0)
        raise FileNotFoundError('You must supply a test ID or include it in the path')

    def upload(p: Path):
        with open(p, 'rb') as data:
            controller.upload(test_id=identifier, filename=p.name, data=data.read(), binary=True)
            click.secho(f'Uploaded {path}', fg='green')

    identifier = test or test_id()
    
    if Path(path).is_file():
        upload(p=Path(path))
    else:
        for obj in Path(path).rglob('*'):
            upload(p=Path(obj))


@build.command('map')
@click.argument('test')
@click.argument('identifier')
@click.pass_obj
@handle_api_error
def map(controller, test, identifier):
    """ Map an identifier to a test """
    print_json(data=controller.map(test_id=test, x=identifier))


@build.command('unmap')
@click.argument('test')
@click.argument('identifier')
@click.pass_obj
@handle_api_error
def unmap(controller, test, identifier):
    """ Unmap an identifier from a test """
    print_json(data=controller.unmap(test_id=test, x=identifier))
