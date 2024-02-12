import re
import uuid
import click
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from rich import print_json
from pathlib import Path, PurePath
from datetime import datetime, timezone

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
@click.option('-q', '--technique', help='MITRE ATT&CK code [e.g. T1557]', default=None, type=str)
@click.option('-a', '--advisory', default=None, hidden=True, type=str)
@click.pass_obj
@handle_api_error
def create_test(controller, name, unit, test, technique, advisory):
    """ Create or update a security test """
    def create_template(template, name):
        utc_time = str(datetime.now(timezone.utc))
        template_body = pkg_resources.read_text(templates, template)
        template_body = template_body.replace('$ID', t['id'])
        template_body = template_body.replace('$NAME', t['name'])
        template_body = template_body.replace('$UNIT', t['unit'])
        template_body = template_body.replace('$TIME', utc_time)
        
        with Spinner(description='Applying default template to new test'):
            controller.upload(test_id=t['id'], filename=name, data=template_body.encode('utf-8'))
            t['attachments'] += [name]

        dir = PurePath(t['id'], name)
        
        with open(dir, 'w', encoding='utf8') as code:
            code.write(template_body)

    with Spinner(description='Creating new test'):
        t = controller.create_test(
            name=name,
            unit=unit,
            test_id=test,
            technique=technique,
            advisory=advisory
        )

    if not test:
        Path(t['id']).mkdir(parents=True, exist_ok=True)
        create_template(template='template.go', name=f'{t["id"]}.go')
        create_template(template='README.md', name='README.md')

    print_json(data=t)


@build.command('update-test')
@click.argument('test')
@click.option('-n', '--name', help='test name', default=None, type=str)
@click.option('-u', '--unit', help='unit identifier', default=None, type=str)
@click.option('-q', '--technique', help='MITRE ATT&CK code [e.g. T1557]', default=None, type=str)
@click.option('-a', '--advisory', help='alert identifier [CVE ID, Advisory ID, etc]', default=None, hidden=True, type=str)
@click.pass_obj
@handle_api_error
def update_test(controller, test, name, unit, technique, advisory):
    """ Create or update a security test """
    with Spinner(description='Updating test'):
        data = controller.update_test(
            test_id=test,
            name=name,
            unit=unit,
            technique=technique,
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
