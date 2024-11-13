from prelude_sdk.controllers.http_controller import HttpController

from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control


class ScmController(HttpController):

    def __init__(self, account):
        super().__init__()
        self.account = account

    @verify_credentials
    def endpoints(self, partner: Control, filter: str, orderby: str, top: int):
        """ Get a list of endpoints from a partner with SCM analysis """
        params = {
            '$filter': filter,
            '$orderby': orderby,
            '$top': top
        }
        res = self._session.get(
            f'{self.account.hq}/scm/endpoints/{partner.name}',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def evaluation_summary(self):
        """ Get policy evaluation summary for all partners """
        res = self._session.get(
            f'{self.account.hq}/scm/evaluation_summary',
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def evaluation(self, partner: Control):
        """ Get policy evaluations for given partner """
        res = self._session.get(
            f'{self.account.hq}/scm/evaluation/{partner.name}',
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_evaluation(self, partner: Control):
        """ Update policy evaluations for given partner """
        res = self._session.post(
            f'{self.account.hq}/scm/evaluation/{partner.name}',
            headers=self.account.headers,
            timeout=60
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
