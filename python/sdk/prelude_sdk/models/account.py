import configparser
import os
from functools import wraps
from os.path import exists
from pathlib import Path

import requests


def verify_credentials(func):
    @wraps(verify_credentials)
    def handler(*args, **kwargs):
        try:
            cfg = args[0].account.read_keychain_config()
            args[0].account.profile = next(
                s for s in cfg.sections() if s == args[0].account.profile
            )
            args[0].account.hq = cfg.get(args[0].account.profile, "hq")
            args[0].account.headers = dict(
                account=cfg.get(args[0].account.profile, "account"),
                token=cfg.get(args[0].account.profile, "token"),
                _product="py-sdk",
                _product_version="2.5.25",
            )
            return func(*args, **kwargs)
        except FileNotFoundError:
            raise Exception(
                "Please create a %s file" % args[0].account.keychain_location
            )
        except KeyError as e:
            raise Exception("Property not found, %s" % e)
        except StopIteration:
            raise Exception(
                'Could not find "%s" profile in %s'
                % (args[0].account.profile, args[0].account.keychain_location)
            )

    handler.__wrapped__ = func
    return handler


class Account:

    def __init__(
        self,
        profile="default",
        hq="https://api.preludesecurity.com",
        keychain_location=os.path.join(Path.home(), ".prelude", "keychain.ini"),
    ):
        self.profile = profile
        self.hq = hq
        self.headers = dict()
        self.keychain_location = keychain_location

    def configure(
        self,
        account_id,
        token,
        handle,
        hq="https://api.preludesecurity.com",
        profile="default",
    ):
        cfg = self._merge_configs(
            self.read_keychain_config(hq, profile),
            self.generate_config(account_id, token, hq, handle, profile),
        )
        self.write_keychain_config(cfg=cfg)

    def read_keychain_config(
        self, hq="https://api.preludesecurity.com", profile="default"
    ):
        if not exists(self.keychain_location):
            head, _ = os.path.split(Path(self.keychain_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            open(self.keychain_location, "x").close()
            self.configure("", "", hq, profile)
        cfg = configparser.ConfigParser()
        cfg.read(self.keychain_location)

        changed = False
        for section in cfg.sections():
            if cfg.get(section, "handle", fallback=None):
                continue
            res = requests.get(
                f"{cfg.get(section, 'hq')}/iam/account",
                headers=dict(
                    account=cfg.get(section, "account"),
                    token=cfg.get(section, "token"),
                    _product="py-sdk",
                ),
                timeout=10,
            )
            if res.status_code == 200:
                changed = True
                cfg[section]["handle"] = res.json()["whoami"]
        if changed:
            self.write_keychain_config(cfg)

        return cfg

    def write_keychain_config(self, cfg):
        with open(self.keychain_location, "w") as f:
            cfg.write(f)

    @staticmethod
    def generate_config(account_id, token, hq, handle, profile):
        cfg = configparser.ConfigParser()
        cfg[profile] = {
            "hq": hq,
            "account": account_id,
            "token": token,
            "handle": handle,
        }
        return cfg

    @staticmethod
    def _merge_configs(cfg_from, cfg_to):
        for section in cfg_from.sections():
            if section not in cfg_to:
                cfg_to[section] = {k: cfg_from[section][k] for k in cfg_from[section]}
        return cfg_to
