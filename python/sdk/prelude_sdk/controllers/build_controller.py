import requests

from prelude_sdk.models.account import verify_credentials


class BuildController:

    def __init__(self, account):
        self.account = account

    @verify_credentials
    def create_test(self, test_id, name, unit, advisory=None):
        """ Create or update a test """
        body = dict(name=name, unit=unit)
        if advisory:
            body['advisory'] = advisory

        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def delete_test(self, test_id):
        """ Delete an existing test """
        res = requests.delete(
            f'{self.account.hq}/build/tests/{test_id}',
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)

    @verify_credentials
    def upload(self, test_id, file):
        """ Upload a test or attachment """
        res = requests.post(
            f'{self.account.hq}/build/tests/{test_id}/{file.name}',
            headers=self.account.headers,
            timeout=10
        )
        if not res.status_code == 200:
            raise Exception(res.text)
        res = res.json()
        print(res['fields'].keys())

        # import logging
        # from requests_toolbelt.multipart import encoder
        # import http.client as http_client
        # http_client.HTTPConnection.debuglevel = 1
        # logging.basicConfig(filename='mahina.log', level=logging.DEBUG)
        # requests_log = logging.getLogger("requests.packages.urllib3")

        fields_str = " ".join(f"-F '{k}={v}'" for k, v in res["fields"].items())
        print(f"curl -v -X POST {fields_str} -F 'file=@{file}' {res['url']}")

        # with open(file, 'rb') as data:
        #     files = {'file': data}
        try:
            files = {'file': open(file, 'rb')}
            res = requests.post(res['url'], data=res['fields'], files=files)
            print(res.status_code)
            if not res.status_code == 204:
                raise Exception(res.text)
        except Exception as e:
            print(e)