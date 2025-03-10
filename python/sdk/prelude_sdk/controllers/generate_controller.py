from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control


class GenerateController(HttpController):
    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def upload_threat_intel(self, file: str):
        with open(file, "rb") as f:
            body = f.read()
        res = self.post(
            f"{self.account.hq}/generate/threat-intel",
            data=body,
            headers=self.account.headers | {"Content-Type": "application/pdf"},
            timeout=30,
        )
        return res.json()

    @verify_credentials
    def get_threat_intel(self, job_id: str):
        res = self.get(
            f"{self.account.hq}/generate/threat-intel/{job_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def generate_from_partner_advisory(self, partner: Control, advisory_id: str):
        params = dict(advisory_id=advisory_id)
        res = self.post(
            f"{self.account.hq}/generate/partner-advisories/{partner.name}",
            headers=self.account.headers,
            json=params,
            timeout=30,
        )
        return res.json()
