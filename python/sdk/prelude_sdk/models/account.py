import configparser
import os
from functools import wraps
from os.path import exists
from pathlib import Path


def verify_credentials(func):
    @wraps(verify_credentials)
    def handler(*args, **kwargs):
        return func(*args, **kwargs)
    return handler


class Account:
    def __init__(self, account, token, hq='https://api.preludesecurity.com'):
        self.hq = hq
        self.headers = dict(
            account=account,
            token=token,
            _product='py-sdk'
        )
