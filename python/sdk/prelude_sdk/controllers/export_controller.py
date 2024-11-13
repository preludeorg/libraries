from prelude_sdk.controllers.http_controller import HttpController

from prelude_sdk.models.account import verify_credentials


class ExportController(HttpController):

    def __init__(self, account):
        super().__init__()
        self.account = account

    @verify_credentials
    def export_scm(self, export_type: str):
        """ Download partner data as a CSV """
        res = self._session.get(
            f'{self.account.hq}/export/scm/{export_type}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
