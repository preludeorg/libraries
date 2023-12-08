import re
import uuid
import click
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from rich import print_json
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
@click.option('-u', '--unit', required=True, help='unit identifier', type=str)
@click.option('-t', '--test', help='test identifier', default=None, type=str)
@click.option('-q', '--techniques', help='comma-separated list of valid MITRE ATT&CK codes [e.g. T1557,T1040]', default=None, type=str)
@click.option('-a', '--advisory', default=None, hidden=True, type=str)
@click.pass_obj
@handle_api_error
def create_test(controller, name, unit, test, techniques, advisory):
    """ Create or update a security test """
    with Spinner(description='Creating new test'):
        t = controller.create_test(
            name=name,
            unit=unit,
            test_id=test,
            techniques=techniques,
            advisory=advisory
        )

    if not test:
        basename = f'{t["id"]}.go'
        template = pkg_resources.read_text(templates, 'template.go')
        template = template.replace('$ID', t['id'])
        template = template.replace('$NAME', name)
        template = template.replace('$UNIT', unit or '')
        template = template.replace('$CREATED', str(datetime.utcnow()))
        
        with Spinner(description='Applying default template to new test'):
            controller.upload(test_id=t['id'], filename=basename, data=template.encode('utf-8'))
            t['attachments'] = [basename]

        test_dir = PurePath(t['id'], basename)
        Path(t['id']).mkdir(parents=True, exist_ok=True)
        
        with open(test_dir, 'w', encoding='utf8') as test_code:
            test_code.write(template)

    print_json(data=t)


@build.command('update-test')
@click.argument('test')
@click.option('-n', '--name', help='test name', default=None, type=str)
@click.option('-u', '--unit', help='unit identifier', default=None, type=str)
@click.option('-q', '--techniques', help='comma-separated list of valid MITRE ATT&CK codes [e.g. T1557,T1040]', default=None, type=str)
@click.option('-a', '--advisory', help='alert identifier [CVE ID, Advisory ID, etc]', default=None, hidden=True, type=str)
@click.pass_obj
@handle_api_error
def update_test(controller, test, name, unit, techniques, advisory):
    """ Create or update a security test """
    with Spinner(description='Updating test'):
        data = controller.update_test(
            test_id=test,
            name=name,
            unit=unit,
            techniques=techniques,
            advisory=advisory
        )
    print_json(data=data)


@build.command('delete-test')
@click.argument('test')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test):
    """ Delete a test """
    with Spinner(description='Removing test'):
        data = controller.delete_test(test_id=test)
    print_json(data=data)


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
            with Spinner(description='Uploading to test'):
                data = controller.upload(
                    test_id=identifier, 
                    filename=p.name, 
                    data=data.read()
                )
            print_json(data=data)

    identifier = test or test_id()
    
    if Path(path).is_file():
        upload(p=Path(path))
    else:
        for obj in Path(path).rglob('*'):
            try:
                upload(p=Path(obj))
            except ValueError as e:
                click.secho(e.args[0], fg='red')
