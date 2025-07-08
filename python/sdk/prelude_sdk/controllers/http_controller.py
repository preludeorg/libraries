import os
import requests

from requests.adapters import HTTPAdapter, Retry


PRELUDE_BACKOFF_FACTOR = int(os.getenv("PRELUDE_BACKOFF_FACTOR", 30))
PRELUDE_BACKOFF_TOTAL = int(os.getenv("PRELUDE_BACKOFF_TOTAL", 0))


class HttpController(object):
    def __init__(self, account):
        self._session = requests.Session()
        self.account = account

        retry = Retry(
            total=PRELUDE_BACKOFF_TOTAL,
            backoff_factor=PRELUDE_BACKOFF_FACTOR,
            status_forcelist=[429],
        )

        self._session.mount("http://", HTTPAdapter(max_retries=retry))
        self._session.mount("https://", HTTPAdapter(max_retries=retry))

    def resolve_enums(self, data, enum_params: list[tuple]):
        for [enum_class, key] in enum_params:
            self._resolve_enum(data, enum_class, key)

    def _resolve_enum(self, data, enum_class, key):
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._resolve_enum(item, enum_class, key)
        elif isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    if isinstance(v, list):
                        for i, item in enumerate(v):
                            v[i] = enum_class[item].name
                    elif v is not None:
                        data[k] = enum_class[v].name
                elif isinstance(v, dict) or isinstance(v, list):
                    self._resolve_enum(v, enum_class, key)

    def get(self, url, retry=True, **kwargs):
        res = self._session.get(url, **kwargs)
        if res.status_code == 200:
            return res
        if res.status_code == 401 and retry and self.account.token_location:
            self.account.refresh_tokens()
            self.account.update_auth_header()
            return self.get(url, retry=False, **kwargs)
        raise Exception(res.text)

    def post(self, url, retry=True, **kwargs):
        res = self._session.post(url, **kwargs)
        if res.status_code == 200:
            return res
        if res.status_code == 401 and retry and self.account.token_location:
            self.account.refresh_tokens()
            self.account.update_auth_header()
            return self.post(url, retry=False, **kwargs)
        raise Exception(res.text)

    def delete(self, url, retry=True, **kwargs):
        res = self._session.delete(url, **kwargs)
        if res.status_code == 200:
            return res
        if res.status_code == 401 and retry and self.account.token_location:
            self.account.refresh_tokens()
            self.account.update_auth_header()
            return self.delete(url, retry=False, **kwargs)
        raise Exception(res.text)

    def put(self, url, retry=True, **kwargs):
        res = self._session.put(url, **kwargs)
        if res.status_code == 200:
            return res
        if res.status_code == 401 and retry and self.account.token_location:
            self.account.refresh_tokens()
            self.account.update_auth_header()
            return self.put(url, retry=False, **kwargs)
        raise Exception(res.text)
