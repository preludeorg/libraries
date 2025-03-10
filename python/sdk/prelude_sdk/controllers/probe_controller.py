from prelude_sdk.controllers.http_controller import HttpController


class ProbeController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    def download(self, name: str, dos: str):
        """Download a probe executable"""
        res = self.get(
            f"{self.account.hq}/download/{name}", headers=dict(dos=dos), timeout=10
        )
        return res.text
