import importlib.resources as pkg_resources
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePath

import click
from rich import print_json

import prelude_cli.templates as templates
from prelude_cli.views.shared import handle_api_error, Spinner
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.models.codes import Control


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
@click.pass_obj
@handle_api_error
def create_test(controller, name, unit, test, technique):
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
            technique=technique
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
@click.pass_obj
@handle_api_error
def update_test(controller, test, name, unit, technique):
    """ Create or update a security test """
    with Spinner(description='Updating test'):
        data = controller.update_test(
            test_id=test,
            name=name,
            unit=unit,
            technique=technique
        )
    print_json(data=data)


@build.command('delete-test')
@click.argument('test')
@click.option('-p', '--purge', is_flag=True, help='purge test and associated files')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_test(controller, test, purge):
    """ Delete a test """
    with Spinner(description='Removing test'):
        data = controller.delete_test(test_id=test, purge=purge)
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


@build.command('create-threat')
@click.argument('name')
@click.option('-p', '--published', help='date the threat was published', required=True, type=str)
@click.option('--id', help='identifier', type=str)
@click.option('-s', '--source', help='source of threat (ex. www.cisa.gov)', default=None, type=str)
@click.option('-i', '--source_id', help='ID of the threat, per the source (ex. aa23-075a)', default=None, type=str)
@click.option('-t', '--tests', help='comma-separated list of test IDs', default=None, type=str)
@click.pass_obj
@handle_api_error
def create_threat(controller, name, published, id, source_id, source, tests):
    """ Create a security threat """
    with Spinner(description='Creating new threat'):
        t = controller.create_threat(
            name=name,
            threat_id=id,
            source_id=source_id,
            source=source,
            published=published,
            tests=tests
        )
    print_json(data=t)


@build.command('update-threat')
@click.argument('threat')
@click.option('-n', '--name', help='test name', default=None, type=str)
@click.option('-s', '--source', help='source of threat (ex. www.cisa.gov)', default=None, type=str)
@click.option('-i', '--source_id', help='ID of the threat, per the source (ex. aa23-075a)', default=None, type=str)
@click.option('-p', '--published', help='date the threat was published', default=None, type=str)
@click.option('-t', '--tests', help='comma-separated list of test IDs', default=None, type=str)
@click.pass_obj
@handle_api_error
def update_threat(controller, threat, name,  source_id, source, published, tests):
    """ Create or update a security threat """
    with Spinner(description='Updating threat'):
        data = controller.update_threat(
            threat_id=threat,
            source_id=source_id,
            name=name,
            source=source,
            published=published,
            tests=tests
        )
    print_json(data=data)


@build.command('delete-threat')
@click.argument('threat')
@click.option('-p', '--purge', is_flag=True, help='purge threat')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_threat(controller, threat, purge):
    """ Delete a threat """
    with Spinner(description='Removing threat'):
        data = controller.delete_threat(threat_id=threat, purge=purge)
    print_json(data=data)


@build.command('create-detection')
@click.argument('partner', type=click.Choice([Control.CROWDSTRIKE.name], case_sensitive=False))
@click.option('-r', '--rules', help='CRWD detection rules, as string-formatted json', default=None, type=str)
@click.option('--rules_file', help='CRWD detection rules, from a json file', default=None, type=click.File())
@click.option('-t', '--test', help='ID of the test this detection is for', required=True, type=str)
@click.option('--detection_id', help='detection ID', default=None, type=str)
@click.option('--rule_id', help='rule ID', default=None, type=str)
@click.pass_obj
@handle_api_error
def create_detection(controller, rules, rules_file, test, partner, detection_id, rule_id):
    """ Create an EDR detection rule """
    if (rules and rules_file) or (not rules and not rules_file):
        raise UsageError('Exactly one of --rules and --rules_file must be set')

    with Spinner(description='Creating new detection'):
        t = controller.create_detection(
            rules=json.loads(rules) if rules else json.load(rules_file),
            test_id=test,
            partner=Control[partner],
            detection_id=detection_id,
            rule_id=rule_id
        )
    print_json(data=t)


@build.command('update-detection')
@click.argument('detection')
@click.option('-r', '--rules', help='CRWD detection rules, as string-formatted json', default=None, type=str)
@click.option('--rules_file', help='CRWD detection rules, from a json file', default=None, type=click.File())
@click.option('--test', help='ID of the test this detection is for', default=None, type=str)
@click.pass_obj
@handle_api_error
def update_detection(controller, detection, rules, rules_file, test):
    """ Update a detection rule """
    if rules and rules_file:
        raise UsageError('At most one of --rules and --rules_file must be set')

    if rules or rules_file:
        rules = json.loads(rules) if rules else json.load(rules_file)
    with Spinner(description='Updating detection'):
        data = controller.update_detection(
            rules=rules,
            test_id=test,
            detection_id=detection,
        )
    print_json(data=data)


@build.command('delete-detection')
@click.argument('detection')
@click.confirmation_option(prompt='Are you sure?')
@click.pass_obj
@handle_api_error
def delete_detection(controller, detection):
    """ Delete a detection """
    with Spinner(description='Removing detection'):
        data = controller.delete_detection(detection_id=detection)
    print_json(data=data)
