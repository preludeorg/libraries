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
