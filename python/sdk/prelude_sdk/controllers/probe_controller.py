import requests


class ProbeController:

    def __init__(self, account):
        self.account = account

    def download(self, name: str, dos: str):
        """ Download a probe executable """
        res = requests.get(
            f'{self.account.hq}/download/{name}',
            headers=dict(dos=dos),
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)
        return res.text
