import os
import uuid
import click
import shutil
import socket
import readline
import webbrowser
import prelude_cli.templates as templates
import importlib.resources as pkg_resources

from rich import print
from rich.rule import Rule
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
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.probe_controller import ProbeController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.models.codes import RunCode, ExitCode, Permission, Decision


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

    def splash(self, markdown: str, short: str, helper: str = None):
        print(Rule(short))
        identifier = hash(markdown)
        if not os.getenv('PRELUDE_NOSPLASH') and identifier not in self.cached_splashes:
            self.console.print(Markdown(markdown))
            self.cached_splashes.append(identifier)
            if helper:
                print(Padding(helper, 1))
            return

    @handle_api_error
    def load_tests(self):
        self.tests = {row['id']: row['name'] for row in self.detect.list_tests()}

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


class DeployProbe:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        # register endpoint
        default = socket.gethostname()
        host = input(f'Enter hostname of your probe [{default}]: ') or default

        default = '1-2-3-4'
        serial = input(f'Enter serial number of your probe [{default}]: ') or default

        edr = input(f'[Optional] Enter edr_id of your endpoint: ')

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
        probes = self.wiz.detect.list_endpoints()
        print(f'You have {len(probes)} registered probes')

        menu = OrderedDict()
        for p in probes:
            entry = f'{self.wiz.normalize(p["host"], 50)} {self.wiz.normalize(p["endpoint_id"], 36)}'
            menu[entry] = None
        indexes = TerminalMenu(
            menu,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        ).show()

        for i in indexes:
            self.wiz.detect.delete_endpoint(ident=probes[i]['endpoint_id'])
            print(f'Deleted "{probes[i]["host"]}" ({probes[i]["endpoint_id"]})')


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
        self.wiz.splash(self.SPLASH, "PROBES", helper='Probes are 1 KB processes that run on endpoints and execute security tests')

        menu = OrderedDict()
        menu['Register new probe'] = DeployProbe
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
        print(f'You have {len(queue)} tests scheduled')
        legend = f'{self.wiz.normalize("schedule", 10)} {self.wiz.normalize("tag", 10)} {self.wiz.normalize("started", 15)} {"test"}'
        menu[legend] = None
        for item in queue:
            entry = f'{self.wiz.normalize(RunCode(item["run_code"]).name, 10)} {self.wiz.normalize(item.get("tag"), 10)} {self.wiz.normalize(item["started"], 15)} {self.wiz.convert(item["test"])}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class ScheduleTest:

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
        menu = [r.name for r in RunCode if r != RunCode.INVALID]
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
            print(f'Test [{tests[test_id]}] has been scheduled')
            self.wiz.detect.enable_test(ident=test_id, run_code=run_code, tags=tags)
        print('Probes check in every few hours to retrieve their scheduled tests')


class DescheduleTest:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        queue = self.wiz.detect.list_queue()
        menu = [f'{self.wiz.normalize(self.wiz.convert(q["test"]), 50)} tag: {self.wiz.normalize(q["tag"], 20)}' for q in queue]
        indexes = TerminalMenu(
            menu,
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        ).show()

        for i in indexes:
            self.wiz.detect.disable_test(ident=queue[i]['test'], tags=queue[i]['tag'])
            print(f'Test has been descheduled: [{menu[i]}]')


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
        self.wiz.splash(self.SPLASH, "SCHEDULING", helper='Verified Security Tests are designed to run continuously')

        menu = OrderedDict()
        menu['View schedule'] = ViewSchedule
        menu['Schedule test'] = ScheduleTest
        menu['Deschedule test'] = DescheduleTest

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class ViewDays:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        filters = self.wiz.filters.copy()
        filters['start'] = datetime.combine(datetime.utcnow() - timedelta(days=14), time.min),

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
        rules = self.wiz.detect.describe_activity(view='rules', filters=self.wiz.filters.copy())

        menu = OrderedDict()
        legend = f'{self.wiz.normalize("rule", 35)} {self.wiz.normalize("failed", 15)} {self.wiz.normalize("endpoints", 15)}'
        menu[legend] = None
        for item in rules:
            rule = item.get('rule')
            usage = item.get('usage')
            if usage:
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
        for item in insights[:10]:
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
            legend = f'{self.wiz.normalize("created", 15)} {self.wiz.normalize("user", 20)} {self.wiz.normalize("title", 40)} {"description"}'
            menu[legend] = None
            for item in recommendations:
                entry = f'{self.wiz.normalize(item["created"], 15)} {self.wiz.normalize(item["handle"], 20)} {self.wiz.normalize(item["title"], 40)} {item["description"]}'
                menu[entry] = item
            index = TerminalMenu(menu.keys()).show()

            answer = list(menu.items())
            AddDecision(self.wiz, answer[index][1]).enter()

        else:
            print('No recommendations are available')


class AddDecision:

    def __init__(self, wiz: Wizard, rec: dict):
        self.wiz = wiz
        self.rec = rec

    def enter(self):
        decision = Decision(self.rec['events'][0]['decision']).name if self.rec['events'] else "None"
        print(f'Title: {self.rec["title"]}\nDecision: {decision}\nDescription: {self.rec["description"]}')

        menu = ['cancel', 'approve', 'deny']
        index = TerminalMenu(menu).show()
        if index:
            self.wiz.detect.make_decision(id=self.rec['id'], decision=Decision[menu[index].upper()].value)

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
        self.wiz.splash(self.SPLASH, "RESULTS", helper='Detect records a code for each executed test to explain what happened')

        menu = OrderedDict()
        menu['Full results: open executive dashboard'] = ExecutiveDashboard
        menu['Summary: results by day'] = ViewDays
        menu['Summary: results by rule'] = ViewRules
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
        default = 'Does my defense work?'
        name = input(f'Enter a test name [{default}]: ') or default
        test_id = str(uuid.uuid4())
        self.wiz.build.create_test(test_id=test_id, name=name)

        mapping = Confirm.ask('Add a classification, such as a rule, CVE or ATT&CK technique?')
        if mapping:
            default = 'VSR-2023-0'
            value = input(f'Enter a classification ID [{default}]: ') or default
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
        self.wiz.splash(self.SPLASH, "BUILD", helper='Verified Security Tests (VST) are production-ready TTPs written in Go')

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
        default = 'test@email.com'
        handle = input(f'Enter a user handle. All handles, except for those with SERVICE permissions, must be valid email addresses [{default}]: ') or default
        menu = [p.name for p in Permission if p != Permission.INVALID]
        answer = TerminalMenu(menu).show()
        expires = datetime.utcnow() + timedelta(days=365)

        creds = self.wiz.iam.create_user(handle=handle, permission=answer, expires=expires)
        print(f'Created "{handle}" with token "{creds["token"]}". New users will receive an email to complete verification.')


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


class ListPartners:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        menu = OrderedDict()
        legend = f'{self.wiz.normalize("name", 20)}'
        menu[legend] = None
        for name in account['controls']:
            entry = f'{self.wiz.normalize(name, 20)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()


class AttachPartner:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        print('Learn about integrations: https://docs.preludesecurity.com/docs/defensive-integrations')
        menu = ['crowdstrike']
        answer = TerminalMenu(menu).show()
        name = menu[answer]

        default = 'https://api.us-2.crowdstrike.com'
        api = input(f'API FQDN [{default}]: ') or default

        default = os.getlogin()
        user = input(f'User or client ID [{default}]: ') or default

        default = 'password123'
        secret = input(f'API token [{default}]: ') or default

        print(f'Attaching "{name}" to your account')
        self.wiz.iam.attach_partner(name=name, api=api, user=user, secret=secret)


class DetachPartner:

    def __init__(self, wiz: Wizard):
        self.wiz = wiz

    def enter(self):
        account = self.wiz.iam.get_account()
        partners = account['controls']

        if not partners:
            print('No partners exist for this account')
            return

        menu = TerminalMenu(partners, multi_select=True, show_multi_select_hint=True)
        menu.show()

        for name in menu.chosen_menu_entries:
            print(f'Detaching "{name}" from your account')
            self.wiz.iam.detach_partner(name=name)


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
        self.wiz.splash(self.SPLASH, "IAM", helper='Prelude accounts can contain multiple users with different permissions')

        menu = OrderedDict()
        menu['List users'] = ListUser
        menu['Create user'] = CreateUser
        menu['Delete user'] = DeleteUser
        menu['List partners'] = ListPartners
        menu['Attach partner'] = AttachPartner
        menu['Detach partner'] = DetachPartner
        menu['Delete account'] = DeleteAccount

        while True:
            try:
                index = TerminalMenu(menu.keys(), title=self.title).show()
                answer = list(menu.items())
                answer[index][1](self.wiz).enter()
            except Exception:
                break


class ExecutiveDashboard:

    def __init__(self, wiz: Wizard, title: str = ''):
        self.wiz = wiz
        self.title = title

    def enter(self):
        account = self.wiz.detect.account.headers['account']
        token = self.wiz.detect.account.headers['token']
        webbrowser.open(f'{self.wiz.detect.account.hq}/iam/user?account={account}&token={token}', new=2)


@click.command()
@click.pass_obj
def interactive(account):
    """ Interactive shell for Prelude Detect """
    wizard = Wizard(account=account)
    wizard.splash(HELLO, "WELCOME")
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
                raise PermissionError('Account not found. Would you like to create a Prelude account?')
            
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

            default = 'test@email.com'
            email = input(f'Enter your email handle [{default}]: ') or default
            wizard.iam.new_account(handle=email)
            keychain = PurePath(Path.home(), '.prelude', 'keychain.ini')
            print(f'Account created! Credentials are stored in your keychain: {keychain}')
            print('Check your email to verify your account, then restart the wizard to continue.')
            break
        except Exception as ex:
            wizard.console.print(str(ex), style='red')
            break
