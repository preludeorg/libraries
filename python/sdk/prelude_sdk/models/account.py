import configparser
import json
import os
from datetime import datetime, timezone
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
            tokens = (
                args[0]
                .account.read_tokens()
                .get(cfg.get(args[0].account.profile, "handle"), {})
                .get(cfg.get(args[0].account.profile, "hq"), {})
            )
            if "access_token" not in tokens:
                raise Exception("Please login to continue")
            if datetime.fromtimestamp(tokens["expires"]) < datetime.now(timezone.utc):
                raise Exception(
                    "Access token expired, please either login or refresh token to continue"
                )
            args[0].account.headers = dict(
                account=cfg.get(args[0].account.profile, "account"),
                authorization=f"Bearer {tokens['access_token']}",
                _product="py-sdk",
            )
            args[0].account.handle = cfg.get(args[0].account.profile, "handle")
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
        token_location=os.path.join(Path.home(), ".prelude", "token.json"),
    ):
        self.profile = profile
        self.hq = hq
        self.headers = dict()
        self.keychain_location = keychain_location
        self.token_location = token_location

    def login(self, password):
        cfg = self.read_keychain_config()
        try:
            next(s for s in cfg.sections() if s == self.profile)
        except StopIteration:
            raise Exception(
                'Could not find "%s" profile in %s'
                % (self.profile, self.keychain_location)
            )
        res = requests.post(
            f"{self.hq}/iam/token",
            json=dict(
                username=cfg[self.profile]["handle"],
                password=password,
                auth_flow="password",
            ),
            timeout=10,
        )
        if res.ok:
            tokens = res.json()
            self.write_tokens(cfg[self.profile]["handle"], self.hq, tokens)
        raise Exception(res.text)

    def configure_account(
        self,
        account_id,
        handle,
        hq="https://api.preludesecurity.com",
        profile="default",
    ):
        cfg = self._merge_configs(
            self.read_keychain_config(hq, profile),
            self.generate_config(account_id, handle, hq, profile),
        )
        self.write_keychain_config(cfg=cfg)

    def read_keychain_config(self):
        if not exists(self.keychain_location):
            head, _ = os.path.split(Path(self.keychain_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            open(self.keychain_location, "x").close()
            self.configure_account("", "")
        cfg = configparser.ConfigParser()
        cfg.read(self.keychain_location)
        return cfg

    def write_keychain_config(self, cfg):
        with open(self.keychain_location, "w") as f:
            cfg.write(f)

    def read_tokens(self):
        if not exists(self.token_location):
            head, _ = os.path.split(Path(self.token_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            open(self.token_location, "x").close()
        with open(self.token_location, "r") as f:
            return json.load(f)

    def write_tokens(self, handle, hq, tokens):
        existing_tokens = self.read_tokens()
        if handle not in existing_tokens:
            existing_tokens[handle] = dict()
        existing_tokens[handle][hq] = tokens
        with open(self.token_location, "w") as f:
            json.dump(existing_tokens, f)

    @staticmethod
    def generate_config(account_id, handle, hq, profile):
        cfg = configparser.ConfigParser()
        cfg[profile] = {"hq": hq, "account": account_id, "handle": handle}
        return cfg

    @staticmethod
    def _merge_configs(cfg_from, cfg_to):
        for section in cfg_from.sections():
            if section not in cfg_to:
                cfg_to[section] = {k: cfg_from[section][k] for k in cfg_from[section]}
        return cfg_to
