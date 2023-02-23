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


MARKDOWN_1= """
```go
package main

// This is a Verified Security Test template

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
# My name is Nocturnal and I am the Detect probe for Linux and MacOS.
# Find the full source-code at https://github.com/preludeorg/libraries

while :
do
    temp=$(mktemp)
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ -z "$test" ]; then
        ...
        ...
```
"""

MARKDOWN_3="""
```bash
# Linux & MacOS: https://github.com/preludeorg/libraries/blob/master/shell/probe/nocturnal.sh
export PRELUDE_TOKEN=<TOKEN>
./nocturnal.sh

# Windows: https://github.com/preludeorg/libraries/blob/master/shell/probe/raindrop.ps1
SETX PRELUDE_TOKEN <TOKEN>
powershell raindrop.ps1
```
"""

class Wizard:

    def __init__(self, account):
        # controllers
        self.iam = IAMController(account=account)
        self.build = BuildController(account=account)
        self.detect = DetectController(account=account)
        # instances
        self.tests = dict()
        self.console = Console()
        self.filters = dict(
            start=datetime.combine(datetime.utcnow() - timedelta(days=30), time.min),
            finish=datetime.combine(datetime.utcnow(), time.max)
        )

    def splash(self, markdown: str):
        self.console.print(Markdown(markdown))

    def load_tests(self):
        self.tests = {row['id']: row['name'] for row in self.build.list_tests()}

    def convert(self, i: str):
        return self.tests.get(i, 'DELETED')

    @staticmethod
    def normalize(element: str, chars: int):
        return element.ljust(chars, " ")


def probes(wiz):
    def list_probes():
        def logs(e):
            endpoint_id = e.split(' ')[0]
            filters = wiz.filters.copy()
            filters['endpoints'] = endpoint_id
            logs = wiz.detect.describe_activity(view='logs', filters=filters)
            print(f'{endpoint_id} has {len(logs)} results over the last 30 days')

            # menu: options
            menu = OrderedDict()
            for log in logs:
                entry = f'{wiz.normalize(log["date"], 30)} {wiz.normalize(ExitCode(log["status"]).name, 15)} {wiz.convert(log["test"])}'
                menu[entry] = logs
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

    def deploy_new():
        endpoint_id = Prompt.ask("Enter an identifier for your probe:", default=socket.gethostname())
        m2 = TerminalMenu(
            ['laptop', 'server', 'container', 'red', 'green', 'white', 'amber'],
            multi_select=True,
            show_multi_select_hint=True,
        )
        m2.show()
        tags = list(m2.chosen_menu_entries)
        token = wiz.detect.register_endpoint(name=endpoint_id, tags=",".join(tags))
        wiz.splash(markdown=MARKDOWN_3)
        print(Padding(f'Use an installer above with token {token} to deploy a probe', 1))

    wiz.splash(markdown=MARKDOWN_2)
    print(Padding(f'Probes are 1 kilobyte processes that run on endpoints and execute security tests', 1))

    # menu: options
    menu = OrderedDict()
    menu['View deployed probes'] = list_probes
    menu['Deploy new probe'] = deploy_new
    # menu: display
    index = TerminalMenu(menu.keys()).show()
    answer = list(menu.items())
    answer[index][1]()


def schedule(wiz):
    print('schedule')


def results(wiz):
    print('analysis')


def build(wiz):
    pass


def manage(wiz):
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
    menu['Manage account'] = manage
    menu['Custom tests'] = build
    menu['Open executive dashboard'] = executive

    wizard = Wizard(account=account)
    wizard.splash(markdown=MARKDOWN_1)
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
