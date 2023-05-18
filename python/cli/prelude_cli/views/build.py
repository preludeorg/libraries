import re
import uuid
import click
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from datetime import datetime
from pathlib import Path, PurePath

from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.build_controller import BuildController


UUID = re.compile('[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}')


@click.group()
@click.pass_context
def build(ctx):
    """ Custom security tests """
    ctx.obj = BuildController(account=ctx.obj)


@build.command('create-test')
@click.argument('name')
@click.option('-t', '--test', help='test identifier', default=None, type=str)
@click.option('-u', '--unit', required=True, help='unit identifier', default=None, type=str)
@click.option('-a', '--advisory', help='alert identifier [CVE ID, Advisory ID, etc]', default=None, type=str)
@click.pass_obj
@handle_api_error
def create_test(controller, name, test, unit, advisory):
    """ Create or update a security test """
    test_id = test or str(uuid.uuid4())
    with Spinner():
        controller.create_test(test_id=test_id, name=name, unit=unit, advisory=advisory)

    if not test:
        basename = f'{test_id}.go'
        template = pkg_resources.read_text(templates, 'template.go')
        template = template.replace('$ID', test_id)
        template = template.replace('$NAME', name)
        template = template.replace('$UNIT', unit or '')
        template = template.replace('$CREATED', str(datetime.utcnow()))
        
        with Spinner():
            controller.upload(test_id=test_id, filename=basename, data=template)

        test_dir = PurePath(test_id, basename)
        Path(test_id).mkdir(parents=True, exist_ok=True)
        
        with open(test_dir, 'w', encoding='utf8') as test_code:
            test_code.write(template)
            click.secho(f'Created {basename}', fg='green')


@build.command('delete-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test):
    """ Delete a test """
    with Spinner():
        controller.delete_test(test_id=test)
    click.secho(f'Deleted {test}', fg='green')


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
            with Spinner():
                controller.upload(
                    test_id=identifier, 
                    filename=p.name, 
                    data=data.read(), 
                    binary=True
                )
            click.secho(f'Uploaded {p.name}', fg='green')

    identifier = test or test_id()
    
    if Path(path).is_file():
        upload(p=Path(path))
    else:
        for obj in Path(path).rglob('*'):
            upload(p=Path(obj))
