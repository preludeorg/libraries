import configparser
import json
import os
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import requests


class Keychain:

    def __init__(
        self, keychain_location=os.path.join(Path.home(), ".prelude", "keychain.ini")
    ):
        self.keychain_location = keychain_location
        if not os.path.exists(self.keychain_location):
            head, _ = os.path.split(Path(self.keychain_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            open(self.keychain_location, "x").close()
            self.configure_keychain("", "")

    def read_keychain(self):
        cfg = configparser.ConfigParser()
        cfg.read(self.keychain_location)
        return cfg

    def configure_keychain(
        self,
        account,
        handle,
        hq="https://api.preludesecurity.com",
        profile="default",
    ):
        cfg = self.read_keychain()
        cfg[profile] = {"account": account, "handle": handle, "hq": hq}
        with open(self.keychain_location, "w") as f:
            cfg.write(f)

    def get_profile(self, profile="default"):
        try:
            cfg = self.read_keychain()
            profile = next(s for s in cfg.sections() if s == profile)
            return cfg[profile]
        except StopIteration:
            raise Exception(
                "Could not find profile for account %s in %s"
                % (profile, self.keychain_location)
            )


class Account:

    def __init__(
        self,
        account: str,
        handle: str,
        hq: str,
        token_location=os.path.join(Path.home(), ".prelude", "tokens.json"),
        profile: str | None = None,
    ):
        self.account = account
        self.handle = handle
        self.headers = dict(account=account, _product="py-sdk")
        self.hq = hq
        self.keychain = Keychain()
        self.profile = profile
        self.token_location = token_location
        if not os.path.exists(self.token_location):
            head, _ = os.path.split(Path(self.token_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            with open(self.token_location, "x") as f:
                json.dump({}, f)

    @staticmethod
    def from_keychain(profile: str = "default"):
        return Account(**Keychain().get_profile(profile), profile=profile)

    @staticmethod
    def from_params(
        account: str, handle: str, hq: str = "https://api.preludesecurity.com"
    ):
        return Account(account, handle, hq)

    def _read_tokens(self):
        with open(self.token_location, "r") as f:
            return json.load(f)

    def _save_new_token(self, new_tokens):
        existing_tokens = self._read_tokens()
        if self.handle not in existing_tokens:
            existing_tokens[self.handle] = dict()
        existing_tokens[self.handle][self.hq] = new_tokens
        with open(self.token_location, "w") as f:
            json.dump(existing_tokens, f)

    def _verify_profile(self):
        if self.profile and not any([self.handle, self.account]):
            raise Exception(
                "Please configure your %s profile to continue" % self.profile
            )

    def password_login(self, password):
        self._verify_profile()
        res = requests.post(
            f"{self.hq}/iam/token",
            headers=self.headers,
            json=dict(username=self.handle, password=password, auth_flow="password"),
            timeout=10,
        )
        if res.ok:
            self._save_new_token(res.json())
        raise Exception("Error logging in using password: %s" % res.text)

    def refresh_tokens(self):
        self._verify_profile()
        existing_tokens = self._read_tokens().get(self.handle, {}).get(self.hq, {})
        if not (refresh_token := existing_tokens.get("refresh_token")):
            raise Exception("No refresh token found, please login first to continue")
        res = requests.post(
            f"{self.hq}/iam/token",
            headers=self.headers,
            json=dict(
                refresh_token=refresh_token, username=self.handle, auth_flow="refresh"
            ),
            timeout=10,
        )
        if res.ok:
            self._save_new_token(res.json())
        raise Exception("Error refreshing token: %s" % res.text)

    def get_access_token(self):
        tokens = self._read_tokens().get(self.handle, {}).get(self.hq, {})
        if "access_token" not in tokens:
            raise Exception("Please login to continue")
        if datetime.fromtimestamp(tokens["expires"]) < datetime.now(timezone.utc):
            raise Exception(
                "Access token expired, please either login or refresh token to continue"
            )
        return tokens["access_token"]


def verify_credentials(func):
    @wraps(verify_credentials)
    def handler(*args, **kwargs):
        args[0].account.headers = args[0].account.headers | dict(
            authorization=f"Bearer {args[0].account.get_access_token()}"
        )
        return func(*args, **kwargs)

    handler.__wrapped__ = func
    return handler
