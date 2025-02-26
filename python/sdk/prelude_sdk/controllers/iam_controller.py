from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import Account, verify_credentials
from prelude_sdk.models.codes import Mode, Permission


class IAMController(HttpController):

    def __init__(self, account: Account):
        super().__init__()
        self.account = account

    @verify_credentials
    def get_account(self):
        """Get account properties"""
        res = self._session.get(
            f"{self.account.hq}/iam/account", headers=self.account.headers, timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def reset_password(self, email: str, account_id: str = None):
        """Reset a user's password"""
        data = dict(
            account_id=account_id or self.account.headers["account"], handle=email
        )
        res = self._session.post(
            f"{self.account.hq}/iam/user/admin_reset", json=data, timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def purge_account(self):
        """Delete an account and all things in it"""
        res = self._session.delete(
            f"{self.account.hq}/iam/account", headers=self.account.headers, timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_account(self, mode: Mode = None, company: str = None, slug: str = None):
        """Update properties on an account"""
        body = dict()
        if mode is not None:
            body["mode"] = mode.name
        if company is not None:
            body["company"] = company
        if slug is not None:
            body["slug"] = slug

        res = self._session.put(
            f"{self.account.hq}/iam/account",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def attach_oidc(
        self,
        client_id: str,
        client_secret: str,
        email_attr: str,
        issuer: str,
        oidc_config_url: str,
    ):
        """Attach OIDC to an account"""
        body = dict(
            client_id=client_id,
            client_secret=client_secret,
            email_attr=email_attr,
            issuer=issuer,
            oidc_url=oidc_config_url,
        )

        res = self._session.post(
            f"{self.account.hq}/iam/account/oidc",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def detach_oidc(self):
        """Detach OIDC to an account"""
        res = self._session.delete(
            f"{self.account.hq}/iam/account/oidc",
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def invite_user(
        self,
        permission: Permission,
        email: str,
        name: str = None,
        oidc: bool = False,
    ):
        """Invite a new user to the account"""
        body = dict(permission=permission.name, handle=email, oidc=oidc)
        if name:
            body["name"] = name

        res = self._session.post(
            url=f"{self.account.hq}/iam/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def create_service_user(self, handle):
        """Create a service user"""
        res = self._session.post(
            f"{self.account.hq}/iam/account/service_user",
            json=dict(handle=handle),
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_user(
        self,
        email: str,
        name: str = None,
    ):
        """Update properties on a user"""
        body = dict(handle=email)
        if name is not None:
            body["name"] = name

        res = self._session.put(
            f"{self.account.hq}/iam/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def update_account_user(
        self,
        email: str,
        permission: Permission = None,
    ):
        """Update properties on an account user"""
        body = dict(handle=email)
        if permission is not None:
            body["permission"] = permission.name

        res = self._session.put(
            f"{self.account.hq}/iam/account/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def list_accounts(self):
        """List all accounts"""
        res = self._session.get(
            f"{self.account.hq}/iam/user/account",
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def remove_user(self, handle):
        """Remove user from the account"""
        res = self._session.delete(
            f"{self.account.hq}/iam/account/user",
            json=dict(handle=handle),
            headers=self.account.headers,
            timeout=10,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def purge_user(self):
        """Delete your user"""
        res = self._session.delete(
            f"{self.account.hq}/iam/user", headers=self.account.headers, timeout=10
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)

    @verify_credentials
    def audit_logs(self, days: int = 7, limit: int = 1000):
        """Get audit logs from the last X days"""
        params = dict(days=days, limit=limit)
        res = self._session.get(
            f"{self.account.hq}/iam/audit",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        if res.status_code == 200:
            return res.json()
        raise Exception(res.text)
