import configparser
import json
import os
from functools import wraps
from pathlib import Path

import requests


class Keychain:

    def __init__(
        self,
        keychain_location: str | None = os.path.join(
            Path.home(), ".prelude", "keychain.ini"
        ),
    ):
        self.keychain_location = keychain_location
        if self.keychain_location and not os.path.exists(self.keychain_location):
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
        hq="https://api.us1.preludesecurity.com",
        oidc=None,
        profile="default",
        slug=None,
    ):
        cfg = self.read_keychain()
        cfg[profile] = {"account": account, "handle": handle, "hq": hq}
        if oidc:
            cfg[profile]["oidc"] = oidc
        if slug:
            cfg[profile]["slug"] = slug
        with open(self.keychain_location, "w") as f:
            cfg.write(f)

    def get_profile(self, profile="default") -> dict:
        try:
            cfg = self.read_keychain()
            profile = next(s for s in cfg.sections() if s == profile)
            return dict(cfg[profile].items())
        except StopIteration:
            raise Exception(
                "Could not find profile %s for account in %s"
                % (profile, self.keychain_location)
            )


def exchange_token(
    account: str, handle: str, hq: str, auth_flow: str, auth_params: dict
):
    """
    Two token exchange auth flows:
    1) Password auth: auth_flow = "password", auth_params = {"password": "your_password"}
    2) Refresh token auth: auth_flow = "refresh", auth_params = {"refresh_token": "your_refresh_token"}
    3) Exchange an OIDC authorization code for tokens:
       auth_flow = "oauth_code", auth_params = {"code": "your_authorization_code", "verifier": "your_verifier", "source": "cli"}
    """
    res = requests.post(
        f"{hq}/iam/token",
        headers=dict(account=account, _product="py-sdk"),
        json=dict(auth_flow=auth_flow, handle=handle, **auth_params),
        timeout=10,
    )
    if res.status_code == 401:
        raise Exception("Error logging in: Unauthorized")
    if not res.ok:
        raise Exception("Error logging in: %s" % res.text)
    return res.json()


class Account:

    @staticmethod
    def from_keychain(profile: str = "default", resolve_enums: bool = False):
        """
        Create an account object from a pre-configured profile in your keychain file
        """
        keychain = Keychain()
        profile_items = keychain.get_profile(profile)
        if any([item not in profile_items for item in ["account", "handle", "hq"]]):
            raise ValueError(
                "Please make sure you are using an up-to-date profile with the following fields: account, handle, hq"
            )
        return _Account(
            account=profile_items["account"],
            handle=profile_items["handle"],
            hq=profile_items["hq"],
            oidc=profile_items.get("oidc"),
            profile=profile,
            slug=profile_items.get("slug"),
            resolve_enums=resolve_enums,
        )

    @staticmethod
    def from_token(
        account: str,
        handle: str,
        token: str | None = None,
        refresh_token: str | None = None,
        hq: str = "https://api.us1.preludesecurity.com",
        oidc: str | None = None,
        slug: str | None = None,
        resolve_enums: bool = False,
    ):
        """
        Create an account object from an access token or a refresh token
        """
        if not any([token, refresh_token]):
            raise ValueError("Please provide either an access token or a refresh token")
        if refresh_token:
            res = exchange_token(
                account, handle, hq, "refresh", dict(refresh_token=refresh_token)
            )
            token = res["token"]
        return _Account(
            account,
            handle,
            hq,
            keychain_location=None,
            oidc=oidc,
            slug=slug,
            token=token,
            token_location=None,
            resolve_enums=resolve_enums,
        )


class _Account:

    def __init__(
        self,
        account: str,
        handle: str,
        hq: str,
        oidc: str | None = None,
        profile: str | None = None,
        slug: str | None = None,
        token: str | None = None,
        keychain_location: str | None = os.path.join(
            Path.home(), ".prelude", "keychain.ini"
        ),
        token_location: str | None = os.path.join(
            Path.home(), ".prelude", "tokens.json"
        ),
        resolve_enums: bool = False,
    ):
        if token is None and token_location is None:
            raise ValueError(
                "Please provide either an access token or a token location"
            )

        super().__init__()
        self.account = account
        self.handle = handle
        self.headers = dict(account=account, _product="py-sdk")
        self.hq = hq
        self.keychain = Keychain(keychain_location)
        self.oidc = oidc
        self.profile = profile
        self.slug = slug
        self.token = token
        self.token_location = token_location
        self.resolve_enums = resolve_enums
        if self.token_location and not os.path.exists(self.token_location):
            head, _ = os.path.split(Path(self.token_location))
            Path(head).mkdir(parents=True, exist_ok=True)
            with open(self.token_location, "x") as f:
                json.dump({}, f)
        self.source = "cli" if self.oidc else "main"

    @property
    def token_key(self):
        return f"{self.handle}/{self.oidc}" if self.oidc else self.handle

    def _read_tokens(self):
        with open(self.token_location, "r") as f:
            return json.load(f)

    def save_new_token(self, new_tokens):
        existing_tokens = self._read_tokens()
        if self.token_key not in existing_tokens:
            existing_tokens[self.token_key] = dict()
        existing_tokens[self.token_key][self.hq] = new_tokens
        with open(self.token_location, "w") as f:
            json.dump(existing_tokens, f)

    def _verify(self):
        if not self.token_location:
            raise ValueError("Please provide a token location to continue")
        if self.profile and not any([self.handle, self.account]):
            raise ValueError(
                "Please configure your %s profile to continue" % self.profile
            )

    def password_login(self, password, new_password=None):
        self._verify()
        tokens = exchange_token(
            self.account,
            self.handle,
            self.hq,
            "password_change" if new_password else "password",
            dict(password=password, new_password=new_password),
        )
        self.save_new_token(tokens)
        return tokens

    def refresh_tokens(self):
        self._verify()
        existing_tokens = self._read_tokens().get(self.token_key, {}).get(self.hq, {})
        if not (refresh_token := existing_tokens.get("refresh_token")):
            raise Exception("No refresh token found, please login first to continue")
        tokens = exchange_token(
            self.account,
            self.handle,
            self.hq,
            "refresh",
            dict(refresh_token=refresh_token, source=self.source),
        )
        tokens = existing_tokens | tokens
        self.save_new_token(tokens)
        return tokens

    def exchange_authorization_code(self, authorization_code: str, verifier: str):
        self._verify()
        tokens = exchange_token(
            self.account,
            self.handle,
            self.hq,
            "oauth_code",
            dict(code=authorization_code, verifier=verifier, source=self.source),
        )
        existing_tokens = self._read_tokens().get(self.token_key, {}).get(self.hq, {})
        tokens = existing_tokens | tokens
        self.save_new_token(tokens)
        return tokens

    def get_token(self):
        if self.token:
            return self.token

        tokens = self._read_tokens().get(self.token_key, {}).get(self.hq, {})
        if "token" not in tokens:
            raise Exception("Please login to continue")
        return tokens["token"]

    def update_auth_header(self):
        self.headers |= dict(authorization=f"Bearer {self.get_token()}")


def verify_credentials(func):
    @wraps(verify_credentials)
    def handler(*args, **kwargs):
        args[0].account.update_auth_header()
        return func(*args, **kwargs)

    handler.__wrapped__ = func
    return handler
