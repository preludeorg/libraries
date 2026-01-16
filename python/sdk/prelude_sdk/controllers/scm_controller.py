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

        res = self.get(f"{self.account.hq}/scm/endpoints", params=params, timeout=30)
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

        res = self.get(f"{self.account.hq}/scm/inboxes", params=params, timeout=30)
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
            f"{self.account.hq}/scm/network_devices", params=params, timeout=30
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

        res = self.get(f"{self.account.hq}/scm/users", params=params, timeout=30)
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
            f"{self.account.hq}/scm/evaluation_summary", params=params, timeout=30
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
            f"{self.account.hq}/scm/evaluations/{partner.name}/{instance_id}"
        )
        return res.json()

    @verify_credentials
    def list_partner_groups(self, filter: str = None, orderby: str = None):
        """List groups"""
        params = {"$filter": filter, "$orderby": orderby}

        res = self.get(f"{self.account.hq}/scm/groups", params=params)
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
            f"{self.account.hq}/scm/groups/{partner.name}/{instance_id}", json=body
        )
        return res.json()

    @verify_credentials
    def list_object_exceptions(self):
        """List object exceptions"""
        res = self.get(f"{self.account.hq}/scm/exceptions/objects")
        exceptions = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(exceptions, [(ControlCategory, "category")])
        return exceptions

    @verify_credentials
    def create_object_exception(
        self, category: ControlCategory, filter, comment=None, name=None, expires: str = None
    ):
        """Create an object exception"""
        body = dict(category=category.name, filter=filter)
        if comment:
            body["comment"] = comment
        if name:
            body["name"] = name
        if expires:
            body["expires"] = expires

        res = self.post(f"{self.account.hq}/scm/exceptions/objects", json=body)
        return res.json()

    @verify_credentials
    def update_object_exception(
        self, exception_id, comment=None, expires=default, filter=None, name=None
    ):
        """Update an object exception"""
        body = dict()
        if comment:
            body["comment"] = comment
        if expires != self.default:
            body["expires"] = expires
        if filter:
            body["filter"] = filter
        if name:
            body["name"] = name

        res = self.post(
            f"{self.account.hq}/scm/exceptions/objects/{exception_id}", json=body
        )
        return res.json()

    @verify_credentials
    def delete_object_exception(self, exception_id):
        """Delete an object exception"""
        res = self.delete(f"{self.account.hq}/scm/exceptions/objects/{exception_id}")
        return res.json()

    @verify_credentials
    def list_policy_exceptions(self):
        """List policy exceptions"""
        res = self.get(f"{self.account.hq}/scm/exceptions/policies")
        exceptions = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(
                exceptions, [(Control, "control"), (ControlCategory, "category")]
            )
        return exceptions

    @verify_credentials
    def create_policy_exception(
        self, partner: Control, instance_id: str, policy_id, setting_names, comment=None, expires=None
    ):
        """Create policy exceptions"""
        body = dict(
            control=partner.name,
            comment=comment,
            expires=expires,
            instance_id=instance_id,
            policy_id=policy_id,
            setting_names=setting_names,
        )

        res = self.post(f"{self.account.hq}/scm/exceptions/policies", json=body)
        return res.json()

    @verify_credentials
    def update_policy_exception(
        self,
        partner: Control,
        instance_id: str,
        policy_id,
        comment=None,
        expires=default,
        setting_names=None,
    ):
        """Update policy exceptions"""
        body = dict(control=partner.name, instance_id=instance_id, policy_id=policy_id)
        if comment:
            body["comment"] = comment
        if expires != self.default:
            body["expires"] = expires
        if setting_names:
            body["setting_names"] = setting_names

        res = self.put(f"{self.account.hq}/scm/exceptions/policies", json=body)
        return res.json()

    @verify_credentials
    def delete_policy_exception(self, instance_id: str, policy_id: str):
        """Delete policy exceptions"""
        body = dict(instance_id=instance_id, policy_id=policy_id)

        res = self.delete(f"{self.account.hq}/scm/exceptions/policies", json=body)
        return res.json()

    @verify_credentials
    def list_views(self):
        """List views"""
        res = self.get(f"{self.account.hq}/scm/views")
        views = res.json()
        if self.account.resolve_enums:
            self.resolve_enums(views, [(ControlCategory, "category")])
        return views

    @verify_credentials
    def create_view(self, category: ControlCategory, filter: str, name: str):
        """Create a view"""
        body = dict(category=category.name, filter=filter, name=name)

        res = self.post(f"{self.account.hq}/scm/views", json=body)
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

        res = self.post(f"{self.account.hq}/scm/views/{view_id}", json=body)
        return res.json()

    @verify_credentials
    def delete_view(self, view_id):
        """Delete a view"""
        res = self.delete(f"{self.account.hq}/scm/views/{view_id}")
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

        res = self.post(f"{self.account.hq}/scm/threats", json=body)
        return res.json()

    @verify_credentials
    def delete_threat(self, id):
        """Delete an existing scm threat"""
        res = self.delete(f"{self.account.hq}/scm/threats/{id}")
        return res.json()

    @verify_credentials
    def get_threat(self, id):
        """Get specific scm threat"""
        res = self.get(f"{self.account.hq}/scm/threats/{id}")
        return res.json()

    @verify_credentials
    def list_threats(self):
        """List all scm threats"""
        res = self.get(f"{self.account.hq}/scm/threats")
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
            json=params,
            timeout=30,
        )
        return res.json()

    @verify_credentials
    def list_notifications(self):
        res = self.get(f"{self.account.hq}/scm/notifications")
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
        res = self.delete(f"{self.account.hq}/scm/notifications/{notification_id}")
        return res.json()

    @verify_credentials
    def upsert_notification(
        self,
        control_category: ControlCategory,
        event: PartnerEvents,
        run_code: RunCode,
        scheduled_hour: int,
        days_in_event: int = 0,
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
            days_in_event=days_in_event,
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

        res = self.put(f"{self.account.hq}/scm/notifications", json=body)
        return res.json()

    @verify_credentials
    def list_notations(self):
        """List notations"""
        res = self.get(f"{self.account.hq}/scm/notations")
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

        res = self.get(f"{self.account.hq}/scm/history", params=params)
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

    @verify_credentials
    def get_report(self, report_id: str):
        """Get SCM report by ID"""
        res = self.get(f"{self.account.hq}/scm/reports/{report_id}")
        return res.json()

    @verify_credentials
    def list_reports(self):
        """List SCM reports"""
        res = self.get(f"{self.account.hq}/scm/reports")
        return res.json()

    @verify_credentials
    def delete_report(self, report_id: str):
        """Delete SCM report by ID"""
        res = self.delete(f"{self.account.hq}/scm/reports/{report_id}")
        return res.json()

    @verify_credentials
    def put_report(self, report_data: dict, report_id: str = None):
        """Put SCM report by ID"""
        body = dict(report=report_data, id=report_id)

        res = self.put(f"{self.account.hq}/scm/reports", json=body)
        return res.json()

    @verify_credentials
    def get_chart_data(
        self,
        scm_category: SCMCategory,
        sort_by: str,
        group_by: str,
        group_limit: int,
        display_overrides: dict = None,
        odata_filter: str = None,
        scopes: dict = None,
    ):
        """Get SCM chart data"""
        body = {
            "category": scm_category.name,
            "display_overrides": display_overrides,
            "group_by": group_by,
            "group_limit": group_limit,
            "scopes": scopes,
            "sort_by": sort_by,
        }
        if odata_filter:
            body["$filter"] = odata_filter

        res = self.post(f"{self.account.hq}/scm/reports/data", json=body, timeout=30)
        return res.json()
