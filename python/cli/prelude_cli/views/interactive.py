import os
import uuid
import click
import shutil
import socket
import webbrowser
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from rich import print
from rich.console import Console
from rich.padding import Padding
from rich.markdown import Markdown
from pathlib import Path, PurePath
from collections import OrderedDict
from rich.prompt import Prompt, Confirm
from simple_term_menu import TerminalMenu
from datetime import datetime, timedelta, time

from prelude_cli.views.shared import handle_api_error
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import RunCode, ExitCode, Permission
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.probe_controller import ProbeController
from prelude_sdk.controllers.detect_controller import DetectController


HELLO="""
```go
package main

// This is a Verified Security Test

import (
    Endpoint "github.com/preludeorg/test/endpoint"
)

func test() {
    Endpoint.Stop(100)
}

func clean() {
    Endpoint.Stop(100)
}

func main() {
    Endpoint.Start(test, clean)
}
```
"""


class Wizard:

    def __init__(self, account):
        # SDK controllers
        self.iam = IAMController(account=account)
        self.build = BuildController(account=account)
        self.probe = ProbeController(account=account)
        self.detect = DetectController(account=account)
        # odds & ends
        self.cached_splashes = []
        self.tests = dict()
        self.console = Console()
        self.filters = dict(
            start=datetime.combine(datetime.utcnow() - timedelta(days=30), time.min),
            finish=datetime.combine(datetime.utcnow(), time.max)
        )

    def splash(self, markdown: str, helper: str = None):
        identifier = hash(markdown)
        if identifier not in self.cached_splashes:
            self.console.print(Markdown(markdown))
            self.cached_splashes.append(identifier)
            if helper:
                print(Padding(helper, 1))

    def load_tests(self):
        try:
            self.tests = {row['id']: row['name'] for row in self.detect.list_tests()}
        except Exception:
            pass

    def my_tests(self):
        account_id = self.build.account.headers['account']
        return {te['id']: te['name'] for te in self.detect.list_tests() if te['account_id'] == account_id}
    
    def convert(self, i: str, reverse=False):
        if reverse:
            rvs = dict((v, k) for k, v in self.tests.items())
            return rvs.get(i, 'DELETED')
        return self.tests.get(i, 'DELETED')

    def add_menu(self, menu: OrderedDict, title: str, item):
        menu[title] = item(self, title)

    @staticmethod
    def normalize(element: str, chars: int):
        element = '' if element is None else element
        return f'{element[:chars - 2]}..' if len(element) > chars else (element or '').ljust(chars, " ")


class ViewLogs:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz


    @handle_api_error
    def enter(self, e: str):
        while True:
            try:
                endpoint_id = e.split(' ')[0]
                filters = self.wiz.filters.copy()
                filters['endpoints'] = endpoint_id
                logs = self.wiz.detect.describe_activity(view='logs', filters=filters)
                print(f'> {endpoint_id} has {len(logs)} results over the last 30 days')

                menu = OrderedDict()
                for log in logs:
                    entry = f'{self.wiz.normalize(log["date"], 30)} {self.wiz.normalize(ExitCode(log["status"]).name, 15)} {self.wiz.convert(log["test"])}'
                    menu[entry] = None
                TerminalMenu(menu.keys()).show()
                break
            except Exception:
                break


class ListProbes:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    @handle_api_error
    def enter(self):
        my_probes = self.wiz.detect.describe_activity(view='probes', filters=self.wiz.filters)
        states = {x['state'] for x in my_probes}
        dos = {x['dos'] for x in my_probes}
        tags = {tag for x in my_probes for tag in x['tags']}
        print(f'Last 30 days: {len(my_probes)} probes in {len(states)} states, across {len(dos)} operating systems, with {len(tags)} tags')

        menu = OrderedDict()
        legend = f'{self.wiz.normalize("endpoint_id", 20)} {self.wiz.normalize("os", 15)} {self.wiz.normalize("state", 15)} tags'
        menu[legend] = None
        for probe in my_probes:
            entry = f'{self.wiz.normalize(probe["endpoint_id"], 20)} {self.wiz.normalize(probe["dos"], 15)} {self.wiz.normalize(probe["state"], 15)} {",".join(probe["tags"])}'
            menu[entry] = ViewLogs

        while True:
            try:
                index = TerminalMenu(menu.keys()).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter(e=answer[index][0])
            except Exception:
                break


class DeployProbe:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        # register endpoint
        host = Prompt.ask("Enter hostname of your probe:", default=socket.gethostname())
        serial = Prompt.ask("Enter serial number of your probe:", default='1-2-3-4')
        edr = Prompt.ask("[Optional] Enter edr_id of your endpoint:", default='')

        print(f'Optionally, select a host type tag')
        systems = ['workstation', 'server', 'container', 'cloud']
        menu = TerminalMenu(
            systems,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        tags = list(menu.chosen_menu_entries or [])

        print(f'Optionally, select a host sensitivity level')
        tlp_colors = ['TLP:CLEAR', 'TLP:GREEN', 'TLP:AMBER', 'TLP:AMBER+STRICT', 'TLP:RED']
        menu = TerminalMenu(
            tlp_colors,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        tags = tags + list(menu.chosen_menu_entries or [])

        token = self.wiz.detect.register_endpoint(host=host, serial_num=serial, edr_id=edr, tags=",".join(tags))
        
        # download executable
        probe_options = OrderedDict()
        probe_options['windows'] = 'raindrop'
        probe_options['darwin'] = 'nocturnal'
        probe_options['linux'] = 'nocturnal'

        print('Which probe do you want?')
        index = TerminalMenu(probe_options.keys()).show()
        answer = list(probe_options.items())
        platform = answer[index]
        print(f'Injecting token "{token}" into executable...')
        code = self.wiz.probe.download(name=platform[1], dos=f'{platform[0]}-x86_64')

        # customize probe
        extension = '.ps1' if platform[0] == 'windows' else ''
        auth = f'SETX PRELUDE_TOKEN {token} /M' if platform[0] == 'windows' else f'export PRELUDE_TOKEN={token}'

        custom_probe = PurePath(Path.home(), '.prelude', f'{host}{extension}')
        with open(custom_probe, 'w') as probe_code:
            probe_code.write(f'{auth}\n{code}')
            print(f'Downloaded {custom_probe}')

        print(Padding('Copy your new probe to a host and start it as an executable', 1))


class DeleteProbe:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        my_probes = [entry['endpoint_id'] for entry in self.wiz.detect.list_endpoints()]
        print(f'You have {len(my_probes)} registered probes')
        menu = TerminalMenu(my_probes, multi_select=True, show_multi_select_hint=True)
        menu.show()

        for ep in menu.chosen_menu_entries:
            print(f'Deleting "{ep}"')
            self.wiz.detect.delete_endpoint(ident=ep)


class Probes:

    SPLASH="""
```bash
# My name is Nocturnal and I am the Detect probe for Linux and MacOS
# Find the full source-code at https://github.com/preludeorg/libraries

while :
do
    temp=$(mktemp)
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
```
    """

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    @handle_api_error
    def enter(self):
        self.wiz.splash(self.SPLASH, helper='Probes are 1 KB processes that run on endpoints and execute security tests')

        menu = OrderedDict()
        menu['Register new probe'] = DeployProbe
        menu['View probe results'] = ListProbes
        menu['Delete existing probe'] = DeleteProbe

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class ViewSchedule:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        menu = OrderedDict()
        queue = self.wiz.detect.list_queue()
        print(f'You have {len(queue)} schedules')
        legend = f'{self.wiz.normalize("schedule", 10)} {self.wiz.normalize("tag", 10)} {self.wiz.normalize("started", 15)} {"test"}'
        menu[legend] = None
        for item in queue:
            entry = f'{self.wiz.normalize(RunCode(item["run_code"]).name, 10)} {self.wiz.normalize(item.get("tag"), 10)} {self.wiz.normalize(item["started"], 15)} {self.wiz.convert(item["test"])}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class AddSchedule:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Select tests to schedule')
        menu = TerminalMenu(
            self.wiz.tests.values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        tests = {self.wiz.convert(i, reverse=True): i for i in list(menu.chosen_menu_entries)}

        print('How often do you want to run these tests?')
        menu = [RunCode.DAILY.name, RunCode.WEEKLY.name, RunCode.MONTHLY.name]
        index = TerminalMenu(menu, multi_select=False).show()
        run_code = RunCode[menu[index]].value

        menu = TerminalMenu(
            {tag for probe in self.wiz.detect.list_endpoints() for tag in probe['tags']},
            skip_empty_entries=True,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        print('Apply this schedule to specific probe tags?')
        menu.show()
        tags = ",".join(menu.chosen_menu_entries or [])

        for test_id in tests:
            print(f'Adding schedule for {tests[test_id]}')
            self.wiz.detect.enable_test(ident=test_id, run_code=run_code, tags=tags)
        print('Probes check in every few hours to retrieve their scheduled tests')


class DeleteSchedule:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        menu = TerminalMenu(
            [self.wiz.convert(entry['test']) for entry in self.wiz.detect.list_queue()],
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu.show()

        tests = {self.wiz.convert(i, reverse=True): i for i in list(menu.chosen_menu_entries)}
        for test_id in tests:
            print(f'Removing schedule for {tests[test_id]}')
            self.wiz.detect.disable_test(ident=test_id)


class Schedule:

    SPLASH="""
```python
class RunCode(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
```  
    """

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    @handle_api_error
    def enter(self):
        self.wiz.splash(self.SPLASH, helper='Verified Security Tests are designed to run continuously')

        menu = OrderedDict()
        menu['View schedule'] = ViewSchedule
        menu['Add schedule'] = AddSchedule
        menu['Remove schedule'] = DeleteSchedule

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class FiltersView:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def process(self, filters):
        my_endpoints = self.wiz.detect.describe_activity(view='probes', filters=self.wiz.filters)

        print('Filter results by probe tags?')
        menu = TerminalMenu(
            {tag for probe in my_endpoints for tag in probe['tags']},
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        if menu.chosen_menu_entries:
            filters['tags'] = ",".join(menu.chosen_menu_entries)

        print('Filter results by operating system?')
        menu = TerminalMenu(
            {probe['dos'] for probe in my_endpoints},
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        if menu.chosen_menu_entries:
            filters['dos'] = ",".join(menu.chosen_menu_entries)

        print('Filter results by tests?')
        menu = TerminalMenu(
            self.wiz.tests.values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        if menu.chosen_menu_entries:
            filters['tests'] = ",".join([self.wiz.convert(i, reverse=True) for i in menu.chosen_menu_entries])


class ViewDays:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        filters = self.wiz.filters.copy()
        FiltersView(self.wiz).process(filters)

        days = self.wiz.detect.describe_activity(view='days', filters=filters)
        days.reverse()

        menu = OrderedDict()
        legend = f'{self.wiz.normalize("date", 15)} {self.wiz.normalize("failed", 15)} {self.wiz.normalize("endpoints", 15)}'
        menu[legend] = None
        for item in days:
            entry = f'{self.wiz.normalize(item["date"], 15)} {self.wiz.normalize(str(item["failed"]), 15)} {self.wiz.normalize(str(item["count"]), 15)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class ViewRules:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print(Padding('Detect classifies tests under rules, which analyze the surface area of operating systems', 1))
        rules = self.wiz.detect.describe_activity(view='rules', filters=self.wiz.filters)

        menu = OrderedDict()
        legend = f'{self.wiz.normalize("rule", 35)} {self.wiz.normalize("failed", 15)} {self.wiz.normalize("endpoints", 15)}'
        menu[legend] = None
        for item in rules:
            rule = item.get('rule')
            usage = item.get('usage')
            entry = f'{self.wiz.normalize(rule["label"], 35)} {self.wiz.normalize(str(usage["failed"]), 15)} {self.wiz.normalize(str(usage["count"]), 15)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class ViewInsights:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print(Padding('A computer generated insight exposes the most vulnerable combinations of test and OS', 1))
        insights = self.wiz.detect.describe_activity(view='insights', filters=self.wiz.filters)

        menu = OrderedDict()
        legend = f'{self.wiz.normalize("unprotected", 15)} {self.wiz.normalize("protected", 15)} {self.wiz.normalize("dos", 15)} {"test"}'
        menu[legend] = None
        for item in insights:
            vol = item['volume']
            if vol['unprotected']:
                entry = f'{self.wiz.normalize(str(vol["unprotected"]), 15)} {self.wiz.normalize(str(vol["protected"]), 15)} {self.wiz.normalize(item["dos"], 15)} {self.wiz.convert(item["test"])}'
                menu[entry] = None
        TerminalMenu(menu.keys()).show()


class ViewRecommendations:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print(Padding('The Prelude team provides manual security recommendations for licensed accounts', 1))
        menu = OrderedDict()
        recommendations = self.wiz.detect.recommendations()

        if recommendations:
            for item in recommendations:
                entry = f'{self.wiz.normalize(item["created"], 15)} {self.wiz.normalize(item["handle"], 20)} {self.wiz.normalize(item["title"], 50)} {item["description"]}'
                menu[entry] = None
            TerminalMenu(menu.keys()).show()
        else:
            print('No recommendations are available')


class Results:

    SPLASH="""
```python
PROTECTED = 100
UNPROTECTED = 101
TIMEOUT = 102
CLEANUP_ERROR = 103
NOT_RELEVANT = 104
QUARANTINED_1 = 105
OUTBOUND_SECURE = 106
EXPLOIT_PREVENTED = 107
```  
    """

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    @handle_api_error
    def enter(self):
        self.wiz.splash(self.SPLASH, helper='Detect records a code for each executed test to explain what happened')

        menu = OrderedDict()
        menu['Results by day'] = ViewDays
        menu['Results by rule'] = ViewRules
        menu['Computer insights'] = ViewInsights
        menu['Human recommendations'] = ViewRecommendations

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class DownloadTests:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Prelude tests are immutable but you can download their source code')
        menu = TerminalMenu(
            self.wiz.tests.values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True)
        menu.show()

        for name in menu.chosen_menu_entries:
            test_id = self.wiz.convert(name, reverse=True)
            workspace = PurePath(Path.home(), '.prelude', 'workspace', test_id)
            Path(workspace).mkdir(parents=True, exist_ok=True)
            test = self.wiz.build.get_test(test_id=test_id)

            for attachment in test.get('attachments'):
                if Path(attachment).suffix:
                    code = self.wiz.build.download(test_id=test_id, filename=attachment)
                    with open(PurePath(workspace, attachment), 'wb') as test_code:
                        test_code.write(code)
            print(f'Downloading {workspace} ({name})')


class CreateTest:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Tests should be in the form of a question')
        # save test
        name = Prompt.ask('Enter a test name', default='Does my defense work?')
        test_id = str(uuid.uuid4())
        self.wiz.build.create_test(test_id=test_id, name=name)

        mapping = Confirm.ask('Add a classification, such as a rule, CVE or ATT&CK technique?')
        if mapping:
            value = Prompt.ask('Enter a classification ID', default='VSR-2023-0')
            self.wiz.build.map(test_id=test_id, x=value.replace(' ', ''))

        # construct test file
        basename = f'{test_id}.go'
        template = pkg_resources.read_text(templates, 'template.go')
        template = template.replace('$ID', test_id)
        template = template.replace('$NAME', name)
        template = template.replace('$CREATED', str(datetime.utcnow()))

        # write test file
        workspace = PurePath(Path.home(), '.prelude', 'workspace', test_id)
        print(workspace)
        Path(workspace).mkdir(parents=True, exist_ok=True)
        with open(PurePath(workspace, basename), 'w') as test_code:
            test_code.write(template)
        self.wiz.load_tests()
        

class DeleteTest:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Deleting tests is permanent and effective immediately')
        menu = TerminalMenu(
            self.wiz.my_tests().values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True)
        menu.show()

        for test in menu.chosen_menu_entries:
            test_id = self.wiz.convert(test, reverse=True)
            print(f'Deleting "{test}"')
            self.wiz.build.delete_test(test_id=test_id)
            shutil.rmtree(PurePath(Path.home(), '.prelude', 'workspace', test_id))
        self.wiz.load_tests()


class UploadTest:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Tests must be uploaded before they can be scheduled')
        my_tests = list(self.wiz.my_tests().items())
        if not my_tests:
            print('You have no custom tests to upload')
            return

        menu = TerminalMenu(
            [f'{self.wiz.normalize(t, 30)} (id: {id})' for id, t in my_tests],
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True)
        indexes = menu.show()

        for i in indexes:
            test_id, test = my_tests[i]
            workspace = PurePath(Path.home(), '.prelude', 'workspace', test_id)

            attachments = list(Path(workspace).glob('*'))
            if not attachments:
                print(f'Workspace missing test: {workspace}')
                continue

            print(f'Uploading {workspace} ({test})')
            for fp in attachments:
                with open(fp, 'r') as attachment:
                    name = Path(fp).name
                    self.wiz.build.upload(test_id=test_id, filename=name, code=attachment.read())


class Build:

    SPLASH="""
```bash
# Find all open-source tests at https://github.com/preludeorg/test

[+] Extracting file for quarantine test
[+] Pausing for 1 second to gauge defensive reaction
[-] Malicious file was not caught!
```  
    """

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    @handle_api_error
    def enter(self):
        self.wiz.splash(self.SPLASH, helper='Verified Security Tests (VST) are production-ready TTPs written in Go')

        menu = OrderedDict()
        menu['Create new test'] = CreateTest
        menu['Upload test'] = UploadTest
        menu['Download test'] = DownloadTests
        menu['Delete test'] = DeleteTest

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class ListUser:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        menu = OrderedDict()
        legend = f'{self.wiz.normalize("handle", 20)} {self.wiz.normalize("permission", 10)} {self.wiz.normalize("expires", 26)}'
        menu[legend] = None
        for user in account['users']:
            handle = user['handle']
            permission = Permission(user['permission']).name
            expires = user['expires']
            entry = f'{self.wiz.normalize(handle, 20)} {self.wiz.normalize(permission, 10)} {self.wiz.normalize(expires, 26)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class CreateUser:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('All users share an account ID but have unique access tokens')
        handle = Prompt.ask('Enter a user handle', default=os.getlogin())
        menu = [p.name for p in Permission if p != Permission.INVALID]
        answer = TerminalMenu(menu).show()
        expires = datetime.utcnow() + timedelta(days=365)

        creds = self.wiz.iam.create_user(handle=handle, permission=answer, expires=expires)
        print(f'Created "{handle}" with token "{creds["token"]}"')


class DeleteUser:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        menu = TerminalMenu(
            [user['handle'] for user in account['users']],
            multi_select=True,
            show_multi_select_hint=True
        )
        menu.show()

        for handle in menu.chosen_menu_entries:
            print(f'Deleting "{handle}"')
            self.wiz.iam.delete_user(handle=handle)


class ListControls:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        menu = OrderedDict()
        legend = f'{self.wiz.normalize("name", 20)} {self.wiz.normalize("apî", 40)} {self.wiz.normalize("username", 10)} {self.wiz.normalize("secret", 10)}'
        menu[legend] = None
        for control in account['controls']:
            name = control['name']
            api = control['api']
            username = control['username']
            secret = control['secret']
            entry = f'{self.wiz.normalize(name, 20)} {self.wiz.normalize(api, 40)} {self.wiz.normalize(username, 10)} {self.wiz.normalize(secret, 10)} '
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class AttachControl:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Learn about integrations: https://docs.preludesecurity.com/docs/defensive-integrations')
        menu = ['crowdstrike']
        answer = TerminalMenu(menu).show()

        name = menu[answer]
        api = Prompt.ask('API FQDN', default='https://api.us-2.crowdstrike.com')
        user = Prompt.ask('User or client ID', default=os.getlogin())
        secret = Prompt.ask('API token', default='password123')
        print(f'Attaching "{name}" to your account')
        self.wiz.iam.attach_control(name=name, api=api, user=user, secret=secret)


class DetachControl:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        controls = [ctrl['name'] for ctrl in account['controls']]

        if not controls:
            print('No controls exist for this account')
            return

        menu = TerminalMenu(controls, multi_select=True, show_multi_select_hint=True)
        menu.show()

        for name in menu.chosen_menu_entries:
            print(f'Detaching "{name}" from your account')
            self.wiz.iam.detach_control(name=name)


class DeleteAccount:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        users = [user for user in account['users']]
        if Confirm.ask(f'Deleting an account is a permanent action which will impact {len(users)} users. Are you sure?'):
            self.wiz.iam.purge_account()
            shutil.rmtree(PurePath(Path.home(), '.prelude'))
            quit()


class IAM:

    SPLASH="""
```javascript
export const Permissions = {
  ADMIN: 0,  // full access 
  EXECUTIVE: 1, // read-only to dashboard
  BUILD: 2,  // executive permissions + developer hub access
  SERVICE: 3, // register new endpoints
  PRELUDE: 4  // read-only access to the results API
  NONE: 5,
} as const;
```  
    """

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    @handle_api_error
    def enter(self):
        self.wiz.splash(self.SPLASH, helper='Prelude accounts can contain multiple users with different permissions')

        menu = OrderedDict()
        menu['List users'] = ListUser
        menu['Create user'] = CreateUser
        menu['Delete user'] = DeleteUser
        menu['List integrations'] = ListControls
        menu['Attach integration'] = AttachControl
        menu['Detach integration'] = DetachControl
        menu['Delete account'] = DeleteAccount

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class ExecutiveDashboard:

    def __init__(self, wiz: Wizard, title: str):
        self.wiz = wiz
        self.title = title

    def enter(self):
        webbrowser.open('https://platform.preludesecurity.com/detect', new=2)


@click.command()
@click.pass_obj
def interactive(account):
    """ Interactive shell for Prelude Detect """
    wizard = Wizard(account=account)
    wizard.splash(HELLO)
    wizard.load_tests()
    print(Padding(f'Your account has access to {len(wizard.tests)} Verified Security Tests', 1))

    menu = OrderedDict()
    wizard.add_menu(menu, 'Deploy probes', Probes)
    wizard.add_menu(menu, 'Schedule tests', Schedule)
    wizard.add_menu(menu, 'View results', Results)
    wizard.add_menu(menu, 'Developer hub', Build)
    wizard.add_menu(menu, 'Manage account', IAM)
    wizard.add_menu(menu, 'Open executive dashboard', ExecutiveDashboard)

    while True:
        try:
            if not wizard.tests:
                raise PermissionError('No local keychain found. Would you like to create a Prelude account?')
            
            index = TerminalMenu(menu.keys()).show()
            answer = list(menu.items())
            answer[index][1].enter()
        except TypeError:
            print(Padding('Goodbye. May Verified Security Tests be with you.', 1))
            break
        except PermissionError as pe:
            yes = Confirm.ask(str(pe))
            if not yes:
                break

            wizard.iam.new_account(handle=os.getlogin())
            keychain = PurePath(Path.home(), '.prelude', 'keychain.ini')
            print(f'Account created! Credentials are stored in your keychain: {keychain}')
        except Exception as ex:
            wizard.console.print(str(ex), style='red')
            break
