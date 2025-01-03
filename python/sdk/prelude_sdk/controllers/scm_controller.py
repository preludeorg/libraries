from prelude_sdk.controllers.http_controller import HttpController

from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control, ControlCategory


class ScmController(HttpController):
    default = -1

    def __init__(self, account):
        super().__init__()
        self.account = account

    @verify_credentials
    def endpoints(self, filter: str = None, orderby: str = None, top: int = None):
        """ List endpoints with SCM analysis """
        params = {
            '$filter': filter,
            '$orderby': orderby,
            '$top': top
        }
        res = self._session.get(
            f'{self.account.hq}/scm/endpoints',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def inboxes(self, filter: str = None, orderby: str = None, top: int = None):
        """ List inboxes with SCM analysis """
        params = {
            '$filter': filter,
            '$orderby': orderby,
            '$top': top
        }
        res = self._session.get(
            f'{self.account.hq}/scm/inboxes',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def users(self, filter: str = None, orderby: str = None, top: int = None):
        """ List users with SCM analysis """
        params = {
            '$filter': filter,
            '$orderby': orderby,
            '$top': top
        }
        res = self._session.get(
            f'{self.account.hq}/scm/users',
            headers=self.account.headers,
            params=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def technique_summary(self, techniques: str):
        """ Get policy evaluation summary by technique """
        res = self._session.get(
            f'{self.account.hq}/scm/technique_summary',
            params=dict(techniques=techniques),
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def evaluation_summary(self, endpoint_filter: str = None, inbox_filter: str = None, user_filter: str = None, techniques: str = None):
        """ Get policy evaluation summary """
        params = dict(
            endpoint_filter=endpoint_filter,
            inbox_filter=inbox_filter,
            user_filter=user_filter,
        )
        if techniques:
            params['techniques'] = techniques
        res = self._session.get(
            f'{self.account.hq}/scm/evaluation_summary',
            params=params,
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def evaluation(self, partner: Control, instance_id: str, filter: str = None, techniques: str = None):
        """ Get policy evaluations for given partner """
        params = {'$filter': filter}
        if techniques:
            params['techniques'] = techniques
        res = self._session.get(
            f'{self.account.hq}/scm/evaluations/{partner.name}/{instance_id}',
            params=params,
            headers=self.account.headers,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_evaluation(self, partner: Control, instance_id: str):
        """ Update policy evaluations for given partner """
        res = self._session.post(
            f'{self.account.hq}/scm/evaluations/{partner.name}/{instance_id}',
            headers=self.account.headers,
            timeout=60
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_object_exceptions(self):
        """ List object exceptions """
        res = self._session.get(
            f'{self.account.hq}/scm/exceptions/objects',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_object_exception(self, category: ControlCategory, filter, name = None, expires: str = None):
        """ Create an object exception """
        body = dict(
            category=category.name,
            filter=filter
        )
        if name:
            body['name'] = name
        if expires:
            body['expires'] = expires
        res = self._session.post(
            f'{self.account.hq}/scm/exceptions/objects',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_object_exception(self, exception_id, expires = default, filter = None, name = None):
        """ Update an object exception """
        body = dict()
        if expires != self.default:
            body['expires'] = expires
        if filter:
            body['filter'] = filter
        if name:
            body['name'] = name
        res = self._session.post(
            f'{self.account.hq}/scm/exceptions/objects/{exception_id}',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_object_exception(self, exception_id):
        """ Delete an object exception """
        res = self._session.delete(
            f'{self.account.hq}/scm/exceptions/objects/{exception_id}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
    
    @verify_credentials
    def list_policy_exceptions(self):
        """ List policy exceptions """
        res = self._session.get(
            f'{self.account.hq}/scm/exceptions/policies',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
    
    @verify_credentials
    def put_policy_exceptions(self, partner: Control, expires, instance_id: str, policy_id, setting_names):
        """ Put policy exceptions """
        body = dict(
            control=partner.name,
            expires=expires,
            instance_id=instance_id,
            policy_id=policy_id,
            setting_names=setting_names
        )
        res = self._session.put(
            f'{self.account.hq}/scm/exceptions/policies',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_scm_threat(self, name, description=None, published=None, techniques=None):
        """ Create an scm threat """
        body = dict(name=name)
        if description:
            body['description'] = description
        if published:
            body['published'] = published
        if techniques:
            body['techniques'] = techniques

        res = self._session.post(
            f'{self.account.hq}/scm/threats',
            json=body,
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def delete_scm_threat(self, name):
        """ Delete an existing scm threat """
        res = self._session.delete(
            f'{self.account.hq}/scm/threats/{name}',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_scm_threats(self):
        """ List all scm threats """
        res = self._session.get(
            f'{self.account.hq}/scm/threats',
            headers=self.account.headers,
            timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def parse_threat_intel(self, file: str):
        with open(file, 'rb') as f:
            body = f.read()
        res = self._session.post(
            f'{self.account.hq}/scm/threat-intel',
            data=body,
            headers=self.account.headers | {'Content-Type': 'application/pdf'},
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def parse_from_partner_advisory(self, partner: Control, advisory_id: str):
        params = dict(advisory_id=advisory_id)
        res = self._session.post(
            f'{self.account.hq}/scm/partner-advisories/{partner.name}',
            headers=self.account.headers,
            json=params,
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
