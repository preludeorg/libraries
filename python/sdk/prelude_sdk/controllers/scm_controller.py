from prelude_sdk.controllers.http_controller import HttpController
from prelude_sdk.models.account import verify_credentials
from prelude_sdk.models.codes import (
    Control,
    ControlCategory,
    PartnerEvents,
    PolicyType,
    NotationType,
    RunCode,
    SCMCategory,
)


class ScmController(HttpController):
    default = "-1"

    def __init__(self, account):
        super().__init__(account)

    @verify_credentials
    def endpoints(self, filter: str = None, orderby: str = None, top: int = None):
        """List endpoints with SCM analysis"""
        params = {"$filter": filter, "$orderby": orderby, "$top": top}
        res = self.get(
            f"{self.account.hq}/scm/endpoints",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                data,
                [
                    (Control, "controls"),
                    (Control, "control"),
                    (ControlCategory, "category"),
                    (PartnerEvents, "event"),
                ],
            )
        return data

    @verify_credentials
    def inboxes(self, filter: str = None, orderby: str = None, top: int = None):
        """List inboxes with SCM analysis"""
        params = {"$filter": filter, "$orderby": orderby, "$top": top}
        res = self.get(
            f"{self.account.hq}/scm/inboxes",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                data,
                [
                    (Control, "controls"),
                    (Control, "control"),
                    (ControlCategory, "category"),
                    (PartnerEvents, "event"),
                ],
            )
        return data

    @verify_credentials
    def network_devices(self, filter: str = None, orderby: str = None, top: int = None):
        """List network_devices with SCM analysis"""
        params = {"$filter": filter, "$orderby": orderby, "$top": top}
        res = self.get(
            f"{self.account.hq}/scm/network_devices",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                data,
                [
                    (Control, "controls"),
                    (Control, "control"),
                    (ControlCategory, "category"),
                    (PartnerEvents, "event"),
                ],
            )
        return data

    @verify_credentials
    def users(self, filter: str = None, orderby: str = None, top: int = None):
        """List users with SCM analysis"""
        params = {"$filter": filter, "$orderby": orderby, "$top": top}
        res = self.get(
            f"{self.account.hq}/scm/users",
            headers=self.account.headers,
            params=params,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                data,
                [
                    (Control, "controls"),
                    (Control, "control"),
                    (ControlCategory, "category"),
                    (PartnerEvents, "event"),
                ],
            )
        return data

    @verify_credentials
    def technique_summary(self, techniques: str):
        """Get policy evaluation summary by technique"""
        res = self.get(
            f"{self.account.hq}/scm/technique_summary",
            params=dict(techniques=techniques),
            headers=self.account.headers,
            timeout=30,
        )
        return res.json()

    @verify_credentials
    def evaluation_summary(
        self,
        endpoint_filter: str = None,
        inbox_filter: str = None,
        user_filter: str = None,
        techniques: str = None,
    ):
        """Get policy evaluation summary"""
        params = dict(
            endpoints_filter=endpoint_filter,
            inboxes_filter=inbox_filter,
            users_filter=user_filter,
        )
        if techniques:
            params["techniques"] = techniques
        res = self.get(
            f"{self.account.hq}/scm/evaluation_summary",
            params=params,
            headers=self.account.headers,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                data, [(Control, "control"), (ControlCategory, "category")]
            )
        return data

    @verify_credentials
    def evaluation(
        self,
        partner: Control,
        instance_id: str,
        filter: str = None,
        policy_types: str = None,
        techniques: str = None,
    ):
        """Get policy evaluations for given partner"""
        params = {"$filter": filter}
        if policy_types:
            params["policy_types"] = policy_types
        if techniques:
            params["techniques"] = techniques
        res = self.get(
            f"{self.account.hq}/scm/evaluations/{partner.name}/{instance_id}",
            params=params,
            headers=self.account.headers,
            timeout=30,
        )
        data = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(data, [(PolicyType, "policy_type")])
        return data

    @verify_credentials
    def update_evaluation(self, partner: Control, instance_id: str):
        """Update policy evaluations for given partner"""
        res = self.post(
            f"{self.account.hq}/scm/evaluations/{partner.name}/{instance_id}",
            headers=self.account.headers,
            timeout=60,
        )
        return res.json()

    @verify_credentials
    def list_partner_groups(self, filter: str = None, orderby: str = None):
        """List groups"""
        params = {"$filter": filter, "$orderby": orderby}
        res = self.get(
            f"{self.account.hq}/scm/groups",
            headers=self.account.headers,
            params=params,
            timeout=10,
        )
        groups = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(groups, [(Control, "control")])
        return groups

    @verify_credentials
    def update_partner_groups(
        self, partner: Control, instance_id: str, group_ids: list[str]
    ):
        """Update groups"""
        body = dict(group_ids=group_ids)
        res = self.post(
            f"{self.account.hq}/scm/groups/{partner.name}/{instance_id}",
            headers=self.account.headers,
            json=body,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_object_exceptions(self):
        """List object exceptions"""
        res = self.get(
            f"{self.account.hq}/scm/exceptions/objects",
            headers=self.account.headers,
            timeout=10,
        )
        exceptions = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(exceptions, [(ControlCategory, "category")])
        return exceptions

    @verify_credentials
    def create_object_exception(
        self, category: ControlCategory, filter, name=None, expires: str = None
    ):
        """Create an object exception"""
        body = dict(category=category.name, filter=filter)
        if name:
            body["name"] = name
        if expires:
            body["expires"] = expires
        res = self.post(
            f"{self.account.hq}/scm/exceptions/objects",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def update_object_exception(
        self, exception_id, expires=default, filter=None, name=None
    ):
        """Update an object exception"""
        body = dict()
        if expires != self.default:
            body["expires"] = expires
        if filter:
            body["filter"] = filter
        if name:
            body["name"] = name
        res = self.post(
            f"{self.account.hq}/scm/exceptions/objects/{exception_id}",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_object_exception(self, exception_id):
        """Delete an object exception"""
        res = self.delete(
            f"{self.account.hq}/scm/exceptions/objects/{exception_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_policy_exceptions(self):
        """List policy exceptions"""
        res = self.get(
            f"{self.account.hq}/scm/exceptions/policies",
            headers=self.account.headers,
            timeout=10,
        )
        exceptions = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                exceptions, [(Control, "control"), (ControlCategory, "category")]
            )
        return exceptions

    @verify_credentials
    def create_policy_exception(
        self, partner: Control, instance_id: str, policy_id, setting_names, expires=None
    ):
        """Create policy exceptions"""
        body = dict(
            control=partner.name,
            expires=expires,
            instance_id=instance_id,
            policy_id=policy_id,
            setting_names=setting_names,
        )
        res = self.post(
            f"{self.account.hq}/scm/exceptions/policies",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def update_policy_exception(
        self,
        partner: Control,
        instance_id: str,
        policy_id,
        expires=default,
        setting_names=None,
    ):
        """Update policy exceptions"""
        body = dict(control=partner.name, instance_id=instance_id, policy_id=policy_id)
        if expires != self.default:
            body["expires"] = expires
        if setting_names:
            body["setting_names"] = setting_names
        res = self.put(
            f"{self.account.hq}/scm/exceptions/policies",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_policy_exception(self, instance_id: str, policy_id: str):
        """Delete policy exceptions"""
        body = dict(instance_id=instance_id, policy_id=policy_id)
        res = self.delete(
            f"{self.account.hq}/scm/exceptions/policies",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_views(self):
        """List views"""
        res = self.get(
            f"{self.account.hq}/scm/views",
            headers=self.account.headers,
            timeout=10,
        )
        views = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(views, [(ControlCategory, "category")])
        return views

    @verify_credentials
    def create_view(self, category: ControlCategory, filter: str, name: str):
        """Create a view"""
        body = dict(category=category.name, filter=filter, name=name)
        res = self.post(
            f"{self.account.hq}/scm/views",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def update_view(
        self, view_id, category: ControlCategory = None, filter=None, name=None
    ):
        """Update a view"""
        body = dict()
        if category:
            body["category"] = category.name
        if filter:
            body["filter"] = filter
        if name:
            body["name"] = name
        res = self.post(
            f"{self.account.hq}/scm/views/{view_id}",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_view(self, view_id):
        """Delete a view"""
        res = self.delete(
            f"{self.account.hq}/scm/views/{view_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def create_threat(
        self,
        name,
        description=None,
        id=None,
        generated=None,
        published=None,
        source=None,
        source_id=None,
        techniques=None,
    ):
        """Create an scm threat"""
        body = dict(name=name)
        if description:
            body["description"] = description
        if id:
            body["id"] = id
        if generated:
            body["generated"] = generated
        if published:
            body["published"] = published
        if source:
            body["source"] = source
        if source_id:
            body["source_id"] = source_id
        if techniques:
            body["techniques"] = techniques

        res = self.post(
            f"{self.account.hq}/scm/threats",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def delete_threat(self, id):
        """Delete an existing scm threat"""
        res = self.delete(
            f"{self.account.hq}/scm/threats/{id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def get_threat(self, id):
        """Get specific scm threat"""
        res = self.get(
            f"{self.account.hq}/scm/threats/{id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_threats(self):
        """List all scm threats"""
        res = self.get(
            f"{self.account.hq}/scm/threats", headers=self.account.headers, timeout=10
        )
        return res.json()

    @verify_credentials
    def parse_threat_intel(self, file: str):
        with open(file, "rb") as f:
            body = f.read()
        res = self.post(
            f"{self.account.hq}/scm/threat-intel",
            data=body,
            headers=self.account.headers | {"Content-Type": "application/pdf"},
            timeout=30,
        )
        return res.json()

    @verify_credentials
    def parse_from_partner_advisory(self, partner: Control, advisory_id: str):
        params = dict(advisory_id=advisory_id)
        res = self.post(
            f"{self.account.hq}/scm/partner-advisories/{partner.name}",
            headers=self.account.headers,
            json=params,
            timeout=30,
        )
        return res.json()

    @verify_credentials
    def list_notifications(self):
        res = self.get(
            f"{self.account.hq}/scm/notifications",
            headers=self.account.headers,
            timeout=10,
        )
        notifications = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                notifications,
                [
                    (ControlCategory, "control_category"),
                    (PartnerEvents, "event"),
                    (RunCode, "run_code"),
                ],
            )
        return notifications

    @verify_credentials
    def delete_notification(self, notification_id: str):
        res = self.delete(
            f"{self.account.hq}/scm/notifications/{notification_id}",
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def upsert_notification(
        self,
        control_category: ControlCategory,
        event: PartnerEvents,
        run_code: RunCode,
        scheduled_hour: int,
        emails: list[str] = None,
        filter: str = None,
        id: str = None,
        message: str = "",
        slack_urls: list[str] = None,
        suppress_empty: bool = True,
        teams_urls: list[str] = None,
        title: str = "SCM Notification",
    ):
        body = dict(
            control_category=control_category.name,
            event=event.name,
            run_code=run_code.name,
            scheduled_hour=scheduled_hour,
            suppress_empty=suppress_empty,
        )
        if id:
            body["id"] = id
        if filter:
            body["filter"] = filter
        if emails:
            body["email"] = dict(emails=emails, message=message, subject=title)
        if slack_urls:
            body["slack"] = dict(hook_urls=slack_urls, message=message)
        if teams_urls:
            body["teams"] = dict(hook_urls=teams_urls, message=message)
        res = self.put(
            f"{self.account.hq}/scm/notifications",
            json=body,
            headers=self.account.headers,
            timeout=10,
        )
        return res.json()

    @verify_credentials
    def list_notations(self):
        """List notations"""
        res = self.get(
            f"{self.account.hq}/scm/notations",
            headers=self.account.headers,
            timeout=10,
        )
        notations = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(notations, [(NotationType, "event")])
        return notations

    @verify_credentials
    def list_history(
        self, start_date: str = None, end_date: str = None, filter: str = None
    ):
        """List history"""
        params = {"start_date": start_date, "end_date": end_date, "$filter": filter}
        res = self.get(
            f"{self.account.hq}/scm/history",
            headers=self.account.headers,
            params=params,
            timeout=10,
        )
        history = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                history,
                [
                    (Control, "control"),
                    (PartnerEvents, "event"),
                    (SCMCategory, "category"),
                ],
            )
        return history
