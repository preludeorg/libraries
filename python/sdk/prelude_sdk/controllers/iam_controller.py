from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import Control, Mode, Permission


class IAMAccountController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def get_account(self):
        """Get account properties"""
        res = self.get(
            f"{self.account.hq}/iam/account", headers=self.account.headers, timeout=10
        )
        account = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                account, [(Mode, "mode"), (Permission, "permission"), (Control, "id")]
            )
        return account

    @verify_credentials
    def purge_account(self):
        """Delete an account and all things in it"""
        res = self.delete(
            f"{self.account.hq}/iam/account", headers=self.account.headers, timeout=10
        )
        return res.json()

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

        res = self.put(
            f"{self.account.hq}/iam/account",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def attach_oidc(
        self,
        client_id: str,
        client_secret: str,
        issuer: str,
        oidc_url: str,
    ):
        """Attach OIDC to an account"""
        email_attr = "email"
        if issuer == "azure":
            email_attr = "upn"
        body = dict(
            client_id=client_id,
            client_secret=client_secret,
            email_attr=email_attr,
            issuer=issuer,
            oidc_url=oidc_url,
        )

        res = self.post(
            f"{self.account.hq}/iam/account/oidc",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def detach_oidc(self):
        """Detach OIDC to an account"""
        res = self.delete(
            f"{self.account.hq}/iam/account/oidc",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def invite_user(
        self,
        email: str,
        oidc: str | None,
        permission: Permission,
        name: str | None = None,
    ):
        """Invite a new user to the account"""
        body = dict(permission=permission.name, handle=email, oidc=oidc)
        if name:
            body["name"] = name

        res = self.post(
            url=f"{self.account.hq}/iam/account/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        user = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(user, [(Permission, "permission")])
        return user

    @verify_credentials
    def create_service_user(self, name: str):
        """Create a service user"""
        body = dict(name=name)

        res = self.post(
            f"{self.account.hq}/iam/account/service_user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_service_user(self, handle: str):
        """Delete service user"""
        body = dict(handle=handle)

        res = self.delete(
            f"{self.account.hq}/iam/account/service_user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def update_account_user(
        self,
        email: str,
        oidc: str | None,
        permission: Permission = None,
    ):
        """Update properties on an account user"""
        body = dict(handle=email, oidc=oidc)
        if permission is not None:
            body["permission"] = permission.name

        res = self.put(
            f"{self.account.hq}/iam/account/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def remove_user(self, email: str, oidc: str | None):
        """Remove user from the account"""
        params = dict(handle=email, oidc=oidc)

        res = self.delete(
            f"{self.account.hq}/iam/account/user",
            params=params,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def audit_logs(self, days: int = 7, limit: int = 1000):
        """Get audit logs from the last X days"""
        params = dict(days=days, limit=limit)
        res = self.get(
            f"{self.account.hq}/iam/audit",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        return res.json()

    def sign_up(self, company, email, name):
        """(NOT AVAIABLE IN PRODUCTION) Create a new user and account"""
        body = dict(company=company, email=email, name=name)

        res = self._session.post(
            f"{self.account.hq}/iam/new_user_and_account",
            headers=self.account.headers,
            json=body,
            timeout=20,
        )
        data = res.json()
        if self.account.profile:
            self.account.keychain.configure_keychain(
                account=data["account_id"],
                handle=data["user_id"],
                hq=self.account.hq,
                profile=self.account.profile,
            )
        return data


class IAMUserController(HttpController):

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def list_accounts(self):
        """List all accounts for your user"""
        res = self.get(
            f"{self.account.hq}/iam/user/account",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def purge_user(self):
        """Delete your user"""
        res = self.delete(
            f"{self.account.hq}/iam/user", headers=self.account.headers, timeout=10
        )
        return res.json()

    @verify_credentials
    def update_user(
        self,
        name: str = None,
    ):
        """Update properties on a user"""
        body = dict()
        if name is not None:
            body["name"] = name

        res = self.put(
            f"{self.account.hq}/iam/user",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    def forgot_password(self):
        """Send a forgot password email"""
        body = dict(handle=self.account.handle)

        res = self.post(
            f"{self.account.hq}/iam/user/forgot_password",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    def confirm_forgot_password(self, confirmation_code: str, new_password: str):
        """Change a password using confirmation code"""
        body = dict(
            handle=self.account.handle,
            confirmation_code=confirmation_code,
            password=new_password,
        )

        res = self.post(
            f"{self.account.hq}/iam/user/forgot_password",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def change_password(self, current_password: str, new_password: str):
        """Change your password"""
        body = dict(current_password=current_password, new_password=new_password)

        res = self.post(
            f"{self.account.hq}/iam/user/change_password",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()
