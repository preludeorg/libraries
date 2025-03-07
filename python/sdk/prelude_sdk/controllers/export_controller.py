from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import SCMCategory


class ExportController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def export_scm(
        self,
        export_type: SCMCategory,
        filter: str = None,
        orderby: str = None,
        top: int = None,
    ):
        """Download partner data as a CSV"""
        params = {
            "$filter": filter,
            "$orderby": orderby,
            "$top": top,
        }
        res = self.post(
            f"{self.account.hq}/export/scm/{export_type.name}",
            params=params,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()
