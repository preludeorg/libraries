import pytest
import uuid

import requests

from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.iam_controller import IAMController
from prelude_sdk.models.codes import Control, Permission


@pytest.fixture(scope="session")
def unwrap():
    def unwrapper(func):
        if not hasattr(func, "__wrapped__"):
            return func
        return unwrapper(func.__wrapped__)

    yield unwrapper


@pytest.fixture(scope="session")
def pause_for_manual_action(pytestconfig):
    class suspend:
        def __init__(self):
            self.capture = pytestconfig.pluginmanager.getplugin("capturemanager")

        def __enter__(self):
            self.capture.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            self.capture.resume_global_capture()

    yield suspend()


def pytest_addoption(parser):
    parser.addoption(
        "--api",
        default="https://api.us2.preludesecurity.com",
        action="store",
        help="API target for tests",
    )
    parser.addoption(
        "--email",
        default="test@auto-accept.developer.preludesecurity.com",
        action="store",
        help="Email address to use for testing",
    )
    parser.addoption(
        "--account_id", action="store", help="Account ID to use for testing"
    )
    parser.addoption(
        "--password",
        action="store",
        help="User password to use for testing. Only used in conjunction with --email",
    )


@pytest.fixture(scope="session")
def api(pytestconfig):
    return pytestconfig.getoption("api")


@pytest.fixture(scope="session")
def email(pytestconfig):
    return pytestconfig.getoption("email")


class Keychain:
    def configure_keychain(self, *args, **kwargs):
        pass


class Account:
    def __init__(self, handle, hq, account=""):
        self.account = account
        self.handle = handle
        self.hq = hq
        self.headers = dict(account=account, _product="py-sdk")
        self.token = ""
        self.keychain = Keychain()

    def password_login(self, password, new_password=None):
        body = dict(
            auth_flow="password_change" if new_password else "password",
            handle=self.handle,
            password=password,
        )
        if new_password:
            body["new_password"] = new_password

        res = requests.post(
            f"{self.hq}/iam/token",
            headers=self.headers,
            json=body,
            timeout=10,
        )
        if not res.ok:
            raise Exception("Error logging in using password: %s" % res.text)
        self.token = res.json()["token"]


@pytest.fixture(scope="session")
def existing_account(pytestconfig):
    if (account_id := pytestconfig.getoption("account_id")) and (
        password := pytestconfig.getoption("password")
    ):
        return dict(account_id=account_id, password=password)


@pytest.fixture(scope="session")
def password(pytestconfig):
    return pytestconfig.getoption("password")


@pytest.fixture(scope="session")
def manual(pytestconfig):
    return not pytestconfig.getoption("email").endswith(
        "@auto-accept.developer.preludesecurity.com"
    )


@pytest.fixture(scope="session")
def setup_account(unwrap, email, api, existing_account, password):
    if hasattr(pytest, "expected_account"):
        return

    pytest.account = Account(handle=email, hq=api)
    iam = IAMController(pytest.account)
    if existing_account:
        pytest.account.account = existing_account["account_id"]
        pytest.account.headers["account"] = existing_account["account_id"]
        pytest.account.password_login(existing_account["password"])
        pytest.account.headers["authorization"] = f"Bearer {pytest.account.token}"
        print(f"[account_id: {existing_account['account_id']}]", end=" ")
    else:
        res = iam.sign_up(company="pysdk-tests", email=email, name="Bob")
        password = "pysdktests"
        pytest.account.headers["account"] = res["account_id"]
        pytest.account.password_login(res["temp_password"], password)
        pytest.account.account = res["account_id"]
        pytest.account.headers["authorization"] = f"Bearer {pytest.account.token}"
        print(f'[account_id: {res["account_id"]}]', end=" ")

    pytest.controls = dict()

    service_user = unwrap(iam.create_service_user)(iam, name="pysdktests")
    pytest.service_user_handle = service_user["handle"]
    pytest.service_user_token = service_user["token"]

    second_email = "second@auto-accept.developer.preludesecurity.com"
    invited_user = unwrap(iam.invite_user)(
        iam,
        email=second_email,
        oidc=None,
        permission=Permission.EXECUTIVE,
        name="second",
    )
    pytest.second_user_account = Account(
        handle=second_email, hq=api, account=pytest.account.account
    )
    pytest.second_user_account.password_login(invited_user["temp_password"], password)
    pytest.second_user_account.headers["authorization"] = (
        f"Bearer {pytest.second_user_account.token}"
    )

    pytest.expected_account = unwrap(iam.get_account)(iam)


@pytest.fixture(scope="session")
def setup_test(unwrap):
    if hasattr(pytest, "expected_test"):
        return

    build = BuildController(pytest.account)
    pytest.test_id = str(uuid.uuid4())
    pytest.expected_test = unwrap(build.create_test)(
        build, test_id=pytest.test_id, name="test_name", unit="custom", technique=None
    )


@pytest.fixture(scope="session")
def setup_threat(unwrap):
    if hasattr(pytest, "expected_threat"):
        return

    build = BuildController(pytest.account)
    pytest.threat_id = str(uuid.uuid4())
    tests = [
        "881f9052-fb52-4daf-9ad2-0a7ad9615baf",
        "b74ad239-2ddd-4b1e-b608-8397a43c7c54",
        pytest.test_id,
    ]
    pytest.expected_threat = unwrap(build.create_threat)(
        build,
        name="threat_name",
        published="2023-11-13",
        threat_id=pytest.threat_id,
        source_id="aa23-061a",
        source="https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a",
        tests=",".join(tests),
    )


@pytest.fixture(scope="session")
def setup_detection(unwrap):
    if not pytest.expected_account["features"]["detections"]:
        return
    if hasattr(pytest, "expected_detection"):
        return

    build = BuildController(pytest.account)
    pytest.detection_id = str(uuid.uuid4())
    pytest.detection_rule = """
    title: Suspicious Command Line Usage in Windows
    description: Detects suspicious use of cmd.exe or powershell.exe with commands often used for reconnaissance like directory listing, tree viewing, or searching for sensitive files.
    logsource:
        category: process_creation
        product: windows
    detection:
        selection:
            ParentImage: 'cmd.exe'
        condition: selection
    level: medium
    """

    pytest.expected_detection = unwrap(build.create_detection)(
        build,
        rule=pytest.detection_rule,
        test_id=pytest.test_id,
        detection_id=pytest.detection_id,
        rule_id=str(uuid.uuid4()),
    )


@pytest.fixture(scope="session")
def setup_threat_hunt(unwrap):
    if not pytest.expected_account["features"]["threat_intel"]:
        return
    if hasattr(pytest, "crwd_threat_hunt_id") and hasattr(pytest, "mde_threat_hunt_id"):
        return

    build = BuildController(pytest.account)
    pytest.crwd_threat_hunt_id = str(uuid.uuid4())
    pytest.expected_threat_hunt = unwrap(build.create_threat_hunt)(
        build,
        control=Control.CROWDSTRIKE,
        name="test CRWD threat hunt",
        query="#repo=base_sensor | ImageFileName is not null | ParentBaseFileName is not null",
        test_id=pytest.test_id,
        threat_hunt_id=pytest.crwd_threat_hunt_id,
    )

    pytest.mde_threat_hunt_id = str(uuid.uuid4())
    unwrap(build.create_threat_hunt)(
        build,
        control=Control.DEFENDER,
        name="test MDE threat hunt",
        query="DeviceProcessEvents | where isnotempty(FileName) and isnotempty(InitiatingProcessFolderPath) and isnotempty(DeviceId) | take 5",
        test_id=pytest.test_id,
        threat_hunt_id=pytest.mde_threat_hunt_id,
    )
