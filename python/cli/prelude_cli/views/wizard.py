import click
import socket

from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.console import Console
from collections import OrderedDict
from simple_term_menu import TerminalMenu
from datetime import datetime, timedelta, time

from prelude_sdk.models.codes import RunCode, ExitCode
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController


class Wizard:

    def __init__(self, account):
        # controllers
        self.iam = IAMController(account=account)
        self.build = BuildController(account=account)
        self.detect = DetectController(account=account)
        # instances
        self.tests = {row['id']: row['name'] for row in self.build.list_tests()}
        self.console = Console()
        self.filters = dict(
            start=datetime.combine(datetime.utcnow() - timedelta(days=30), time.min),
            finish=datetime.combine(datetime.utcnow(), time.max)
        )

    def convert(self, i):
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

            my_tests = {row['id']: row['name'] for row in build.list_tests()}
            convert = lambda i: my_tests.get(i, 'DELETED')

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
            ['laptop', 'server', 'container', 'red', 'blue', 'green', 'white', 'amber'],
            multi_select=True,
            show_multi_select_hint=True,
        )
        m2.show()
        tags = list(m2.chosen_menu_entries)
        token = wiz.detect.register_endpoint(name=endpoint_id, tags=",".join(tags))

        text = Text()
        text.append(f"Use the following token to deploy a probe: ")
        text.append(token, style="bold green")
        wiz.console.print(text)
    
    # menu: options
    menu = OrderedDict()
    menu['View deployed probes'] = list_probes
    menu['Deploy new probe'] = deploy_new
    # menu: display
    index = TerminalMenu(menu.keys()).show()
    answer = list(menu.items())
    answer[index][1]()


def schedule(account):
    print('schedule')


def results(account):
    print('analysis')


def build(account):
    pass


def manage(account):
    pass


def executive(account):
    pass


@click.command()
@click.pass_obj
def wizard(account):
    """ Interactive shell for managing Detect """
    menu = OrderedDict()
    menu['Deploy probes'] = probes
    menu['Schedule tests'] = schedule
    menu['View results'] = results
    menu['Manage account'] = manage
    menu['Open executive dashboard'] = executive

    while True:
        try:
            wizard = Wizard(account=account)
            index = TerminalMenu(menu.keys()).show()
            answer = list(menu.items())
            answer[index][1](wiz=wizard)
        except TypeError:
            print('Goodbye!')
            break
