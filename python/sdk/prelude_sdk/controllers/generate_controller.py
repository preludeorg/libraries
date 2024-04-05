import requests

from prelude_sdk.controllers.http_controller import HttpController

from prelude_sdk.models.account import verify_credentials


class GenerateController(HttpController):
    def __init__(self, account):
        super().__init__()
        self.account = account

    @verify_credentials
    def upload_threat_intel(self, file: str):
        with open(file, 'rb') as f:
            body = f.read()
        res = self._session.post(
            f'{self.account.hq}/generate/threat-intel',
            data=body,
            headers=self.account.headers | {'Content-Type': 'application/pdf'},
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def get_threat_intel(self, job_id: str):
        res = self._session.get(
            f'{self.account.hq}/generate/threat-intel/{job_id}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
