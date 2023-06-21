import click

from configparser import ConfigParser, MissingSectionHeaderError


@click.command()
@click.option('-f', '--file', help="path to credentials file (.ini)", default=None, type=click.Path(exists=True))
@click.pass_obj
def configure(account, file):
    """ Configure your local keychain """
    profile = account.profile
    hq = account.hq
    account_id = None
    account_token = None

    if file:
        config = ConfigParser()
        
        try:
            config.read(file)
            profile = config.sections()[0]
            values = config[profile]
            hq = values['hq']
            account_id = values['account']
            account_token = values['token']
        except MissingSectionHeaderError:
            click.secho('Invalid credentials file: No profile header found', fg='red')
            return
        except KeyError as e:
            click.secho('Invalid credentials file: Missing {}'.format(e), fg='red')
            return
        except Exception as e:
            click.secho('Invalid credentials file', fg='red')
            return

        if not account_id or not account_token:
            click.secho('Invalid credentials file: Missing values for account ID and/or account token', fg='red')
            return
        
    else:
        profile = click.prompt('Enter the profile name', default=account.profile, show_default=True)
        hq = click.prompt('Enter the Prelude API', default=account.hq, show_default=True)
        account_id = click.prompt('Enter your account ID')
        account_token = click.prompt('Enter your account token')
         
    account.configure(profile=profile, hq=hq, account_id=account_id, token=account_token)
    click.secho('Credentials saved', fg='green')