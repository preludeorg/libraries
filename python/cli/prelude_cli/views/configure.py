import click
import re
from prelude_cli.views.shared import handle_api_error

import configparser


@click.command()
@click.option('-f', '--file', help="path to credentials file [.ini]", default=None, type=click.Path(exists=True))
@click.pass_obj
def configure(account, file):
    """ Configure your local keychain """
    if file:

        # config = configparser.ConfigParser()
        # config.read('hello.ini')
        # profile = config.sections().index(0)
        # return
        creds = {
            'profile': None,
            'hq': None,
            'account': None,
            'token': None
        }

        with open(file, 'r') as creds_file:
            for ln in creds_file:
                profile_match = re.search(r"(?<=\[).*(?=\])", ln)
                if profile_match:
                    creds['profile'] = profile_match.group(0)
                else:
                    key, val = ln.strip().split('=')
                    key = key.strip()
                    val = val.strip()
                    if key in creds:
                        creds[key] = val

        for _, val in creds.items():
            if val is None:
                click.secho('Invalid credentials file', fg='red')
                return
            
        account.configure(profile=creds['profile'], hq=creds['hq'], account_id=creds['account'], token=creds['token'])
        click.secho('Credentials saved', fg='green')

    else:
        profile = click.prompt('Enter the profile name', default=account.profile, show_default=True)
        hq = click.prompt('Enter the Prelude API', default=account.hq, show_default=True)
        account_id = click.prompt('Enter your account ID')
        account_token = click.prompt('Enter your account token')
        account.configure(profile=profile, hq=hq, account_id=account_id, token=account_token)
        click.secho('Credentials saved', fg='green')
