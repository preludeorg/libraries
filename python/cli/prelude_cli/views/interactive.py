import click
import socket

from rich import print
from rich.prompt import Prompt
from rich.console import Console
from rich.padding import Padding
from rich.markdown import Markdown
from collections import OrderedDict
from simple_term_menu import TerminalMenu
from datetime import datetime, timedelta, time

from prelude_sdk.models.codes import RunCode, ExitCode
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController


MARKDOWN_1="""
```go
package main

// This is a Verified Security Test

import "github.com/preludeorg/test/endpoint"

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

MARKDOWN_2="""
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

MARKDOWN_3="""
```python
class RunCode(Enum):
    DAILY = 1
    WEEKLY = 2
    MONTHLY = 3
```    
"""

MARKDOWN_4="""

"""

class Wizard:

    def __init__(self, account):
        # controllers
        self.iam = IAMController(account=account)
        self.build = BuildController(account=account)
        self.detect = DetectController(account=account)
        # instances
        self.shown_splashes = []
        self.tests = dict()
        self.console = Console()
        self.filters = dict(
            start=datetime.combine(datetime.utcnow() - timedelta(days=30), time.min),
            finish=datetime.combine(datetime.utcnow(), time.max)
        )

    def splash(self, markdown: str, helper: str = None):
        identifier = hash(markdown)
        if identifier not in self.shown_splashes:
            self.console.print(Markdown(markdown))
            self.shown_splashes.append(identifier)
            if helper:
                print(Padding(helper, 1))

    def load_tests(self):
        self.tests = {row['id']: row['name'] for row in self.build.list_tests()}

    def convert(self, i: str, reverse=False):
        if reverse:
            rvs = dict((v, k) for k, v in self.tests.items())
            return rvs.get(i, 'DELETED')
        return self.tests.get(i, 'DELETED')

    @staticmethod
    def normalize(element: str, chars: int):
        return (element or '').ljust(chars, " ")


def probes(wiz):
    def list_probes():
        def logs(e):
            endpoint_id = e.split(' ')[0]
            filters = wiz.filters.copy()
            filters['endpoints'] = endpoint_id
            logs = wiz.detect.describe_activity(view='logs', filters=filters)
            print(f'{endpoint_id} has {len(logs)} results over the last 30 days')

            menu = OrderedDict()
            for log in logs:
                entry = f'{wiz.normalize(log["date"], 30)} {wiz.normalize(ExitCode(log["status"]).name, 15)} {wiz.convert(log["test"])}'
                menu[entry] = None
            TerminalMenu(menu.keys()).show()

        my_probes = wiz.detect.describe_activity(view='probes', filters=wiz.filters)
        states = {x['state'] for x in my_probes}
        dos = {x['dos'] for x in my_probes}
        tags = {tag for x in my_probes for tag in x['tags']}
        print(f'Last 30 days: {len(my_probes)} probes in {len(states)} states, across {len(dos)} operating systems, with {len(tags)} tags')
        
        # menu: options
        menu = OrderedDict()
        for probe in my_probes:
            entry = f'{wiz.normalize(probe["endpoint_id"], 20)} {wiz.normalize(probe["dos"], 15)} {wiz.normalize(probe["state"], 15)} {",".join(probe["tags"])}'
            menu[entry] = logs
        # menu: display
        index = TerminalMenu(menu.keys()).show()
        answer = list(menu.items())
        answer[index][1](e=answer[index][0])

    def delete_probe():
        menu = TerminalMenu(
            [entry['endpoint_id'] for entry in wiz.detect.list_endpoints()],
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu.show()

        for ep in list(menu.chosen_menu_entries):
            wiz.detect.delete_endpoint(ident=ep)

    def deploy_new():
        endpoint_id = Prompt.ask("Enter an identifier for your probe:", default=socket.gethostname())
        menu = TerminalMenu(
            ['laptop', 'server', 'container', 'red', 'green', 'white', 'amber'],
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        tags = menu.chosen_menu_entries or []
        token = wiz.detect.register_endpoint(name=endpoint_id, tags=",".join(tags))
        print('Installers: https://github.com/preludeorg/libraries/tree/master/shell/install')
        print(Padding(f'Use an installer with token {token} to deploy a probe', 1))

    wiz.splash(
        markdown=MARKDOWN_2, 
        helper='Probes are 1 kilobyte processes that run on endpoints and execute security tests'
    )

    # menu: options
    menu = OrderedDict()
    menu['View deployed probes'] = list_probes
    menu['Deploy new probe'] = deploy_new
    menu['Delete existing probe'] = delete_probe
    # menu: display
    index = TerminalMenu(menu.keys()).show()
    answer = list(menu.items())
    answer[index][1]()


def schedule(wiz):
    def list_queue():
        menu = OrderedDict()
        for item in wiz.detect.list_queue():
            entry = f'{wiz.normalize(RunCode(item["run_code"]).name, 10)} {wiz.normalize(item.get("tag"), 10)} {wiz.normalize(item["started"], 15)} {wiz.convert(item["test"])}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()

    def enable_test():
        menu = TerminalMenu(
            wiz.tests.values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        test_names = [wiz.convert(i, reverse=True) for i in list(menu.chosen_menu_entries)]

        menu = [RunCode.DAILY.name, RunCode.WEEKLY.name, RunCode.MONTHLY.name]
        index = TerminalMenu(menu, multi_select=False).show()
        run_code = RunCode[menu[index]].value

        menu = TerminalMenu(
            {tag for probe in wiz.detect.list_endpoints() for tag in probe['tags']},
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        tags = ",".join(menu.chosen_menu_entries)

        for test in test_names:
            wiz.detect.enable_test(ident=test, run_code=run_code, tags=tags)

    def disable_test():
        menu = TerminalMenu(
            [wiz.convert(entry['test']) for entry in wiz.detect.list_queue()],
            multi_select=True,
            show_multi_select_hint=True,
        )
        menu.show()

        for test in [wiz.convert(i, reverse=True) for i in list(menu.chosen_menu_entries)]:
            wiz.detect.disable_test(ident=test)

    wiz.splash(
        markdown=MARKDOWN_3,
        helper='Verified Security Tests can be scheduled according to run codes'
    )
    print(Padding(f'', 1))

    # menu: options
    menu = OrderedDict()
    menu['View schedule'] = list_queue
    menu['Add schedule'] = enable_test
    menu['Remove schedule'] = disable_test
    # menu: display
    index = TerminalMenu(menu.keys()).show()
    answer = list(menu.items())
    answer[index][1]()


def results(wiz):
    def construct(filters):
        my_endpoints = wiz.detect.describe_activity(view='probes', filters=wiz.filters)

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

        menu = TerminalMenu(
            wiz.tests.values(),
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        if menu.chosen_menu_entries:
            filters['tests'] = ",".join([wiz.convert(i, reverse=True) for i in menu.chosen_menu_entries])

        menu = TerminalMenu(
            [c.name for c in ExitCode],
            multi_select=True,
            show_multi_select_hint=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True
        )
        menu.show()
        if menu.chosen_menu_entries:
            filters['statuses'] = ",".join([str(ExitCode[x].value) for i in menu.chosen_menu_entries])

    def days():
        filters = wiz.filters.copy()
        construct(filters=filters)

        days = wiz.detect.describe_activity(view='days', filters=filters)
        days.reverse()

        menu = OrderedDict()
        legend = f'{wiz.normalize("date", 15)} {wiz.normalize("unprotected", 15)} {wiz.normalize("total", 15)}'
        menu[legend] = None
        for item in days:
            entry = f'{wiz.normalize(item["date"], 15)} {wiz.normalize(str(item["unprotected"]), 15)} {wiz.normalize(str(item["count"]), 15)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()

    def rules():
        filters = wiz.filters.copy()
        construct(filters=filters)

        rules = wiz.detect.describe_activity(view='rules', filters=filters)

        menu = OrderedDict()
        legend = f'{wiz.normalize("rule", 35)} {wiz.normalize("unprotected", 15)} {wiz.normalize("total", 15)}'
        menu[legend] = None
        for item in rules:
            rule = item.get('rule')
            usage = item.get('usage')
            entry = f'{wiz.normalize(rule["label"], 35)} {wiz.normalize(str(usage["unprotected"]), 15)} {wiz.normalize(str(usage["count"]), 15)}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()

    def insights():
        filters = wiz.filters.copy()
        construct(filters=filters)

        insights = wiz.detect.describe_activity(view='insights', filters=filters)

        menu = OrderedDict()
        legend = f'{wiz.normalize("unprotected", 15)} {wiz.normalize("protected", 15)} {wiz.normalize("dos", 15)} {"test"}'
        menu[legend] = None
        for item in insights:
            vol = item['volume']
            entry = f'{wiz.normalize(str(vol["unprotected"]), 15)} {wiz.normalize(str(vol["protected"]), 15)} {wiz.normalize(item["dos"], 15)} {wiz.convert(item["test"])}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()

    def recommendations():
        menu = OrderedDict()
        recommendations = wiz.detect.recommendations()

        for item in recommendations:
            entry = f'{wiz.normalize(item["created"]), 15} {wiz.normalize(item["handle"]), 20} {wiz.normalize(item["title"], 50)} {item["description"]}'
            menu[entry] = None
        TerminalMenu(menu.keys()).show()

    wiz.splash(markdown=MARKDOWN_4, helper='Each result is a granular code to reduce telemetry')

    # menu: options
    menu = OrderedDict()
    menu['Results by day'] = days
    menu['Results by rule'] = rules
    menu['Computer insights'] = insights
    menu['Human recommendations'] = recommendations
    # menu: display
    index = TerminalMenu(menu.keys()).show()
    answer = list(menu.items())
    answer[index][1]()

def build(wiz):
    pass


def iam(wiz):
    pass


def executive(wiz):
    pass


@click.command()
@click.pass_obj
def interactive(account):
    """ Interactive shell for managing Detect """
    menu = OrderedDict()
    menu['Deploy probes'] = probes
    menu['Schedule tests'] = schedule
    menu['View results'] = results
    menu['Customize tests'] = build
    menu['Manage account'] = iam
    menu['Open executive dashboard'] = executive

    wizard = Wizard(account=account)
    wizard.splash(MARKDOWN_1)

    wizard.load_tests()
    print(Padding(f'Your account has access to {len(wizard.tests)} Verified Security Tests', 1))

    while True:
        try:
            index = TerminalMenu(menu.keys()).show()
            answer = list(menu.items())
            answer[index][1](wiz=wizard)
        except TypeError:
            print('Goodbye!')
            break
