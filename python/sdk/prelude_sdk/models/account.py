import configparser
import os
from functools import wraps
from os.path import exists
from pathlib import Path


def verify_credentials(func):
    @wraps(verify_credentials)
    def handler(*args, **kwargs):
        try:
            cfg = args[0].account.read_keychain_config()
            args[0].account.profile = next(s for s in cfg.sections() if s == args[0].account.profile)
            args[0].account.hq = cfg.get(args[0].account.profile, 'hq')
            args[0].account.headers = dict(
                account=cfg.get(args[0].account.profile, 'account'),
                token=cfg.get(args[0].account.profile, 'token'),
                _product='py-sdk'
            )
            return func(*args, **kwargs)
        except FileNotFoundError:
            raise Exception('Please create a %s file' % args[0].account.keychain_location)
        except KeyError as e:
            raise Exception('Property not found, %s' % e)
        except StopIteration:
            raise Exception('Could not find "%s" profile in %s' % (args[0].account.profile, args[0].account.keychain_location))
    return handler


class Account:
    def __init__(self, account, token, hq='https://api.preludesecurity.com'):
        self.hq = hq
        self.headers = dict(
            account=account,
            token=token,
            _product='py-sdk'
        )
