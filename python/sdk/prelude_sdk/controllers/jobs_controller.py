from itertools import chain

from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import BackgroundJobTypes, Control


class JobsController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def job_statuses(self):
        """Get job statuses"""
        res = self.get(
            f"{self.account.hq}/jobs/statuses", headers=self.account.headers, timeout=30
        )
        jobs = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(jobs, [(Control, "control")])
        return jobs

    @verify_credentials
    def job_status(self, job_id: str):
        """Get job status given job ID"""
        res = self.get(
            f"{self.account.hq}/jobs/statuses/{job_id}",
            headers=self.account.headers,
            timeout=30,
        )
        job = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                job, [(Control, "control"), (BackgroundJobTypes, "job_type")]
            )
        return job
