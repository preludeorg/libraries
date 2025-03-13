from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials


class JobsController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def job_statuses(self):
        """Get job statuses"""
        res = self.get(
            f"{self.account.hq}/jobs/statuses", headers=self.account.headers, timeout=30
        )
        return res.json()

    @verify_credentials
    def job_status(self, job_id: str):
        """Get job status given job ID"""
        res = self.get(
            f"{self.account.hq}/jobs/statuses/{job_id}",
            headers=self.account.headers,
            timeout=30,
        )
        return res.json()
