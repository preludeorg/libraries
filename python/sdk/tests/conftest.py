import logging
import os
import pytest
import uuid
from pathlib import Path

from prelude_sdk.models.account import _Account
from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.detect_controller import DetectController
from prelude_sdk.controllers.export_controller import ExportController
from prelude_sdk.controllers.generate_controller import GenerateController
from prelude_sdk.controllers.iam_controller import (
    IAMAccountController,
    IAMUserController,
)
from prelude_sdk.controllers.jobs_controller import JobsController
from prelude_sdk.controllers.partner_controller import PartnerController
from prelude_sdk.controllers.probe_controller import ProbeController
from prelude_sdk.controllers.scm_controller import ScmController
from prelude_sdk.models.codes import Control

from testutils import *


def pytest_configure(config):
    marker = f"/{marker}" if (marker := config.getoption("-m")) else ""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    log_dir = Path(f"pytest_logs{marker}")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{worker_id}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(processName)s] [%(levelname)s] %(message)s",
        filename=log_file,
        filemode="w",
        force=True,
    )


def pytest_runtest_logreport(report):
    if report.skipped:
        logging.info(f"Test skipped: {report.nodeid}")
        if report.longrepr:
            reason = (
                report.longrepr[2]
                if isinstance(report.longrepr, tuple)
                else report.longrepr
            )
            logging.info(f"Skip reason: {reason}")

    if report.failed:
        logging.error(f"Test failed: {report.nodeid}")
        logging.error(f"Failure traceback:\n{str(report.longrepr)}")
        # if report.capstderr:
        #     logging.error(f"Captured stderr:\n{report.capstderr}")
        # if report.capstdout:
        #     logging.error(f"Captured stdout:\n{report.capstdout}")
        # if report.longrepr:
        #     logging.error(f"Failure traceback:\n{str(report.longrepr)}")


def pytest_addoption(parser):
    parser.addoption(
        "--api",
        default="https://api.us2.preludesecurity.com",
        action="store",
        help="API target for tests",
    )
    parser.addoption(
        "--email",
        default=f"test-{str(uuid.uuid4())[:12]}@auto-accept.developer.preludesecurity.com",
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
    parser.addoption(
        "--manual", action="store_true", default=False, help="Enable manual tests"
    )
    parser.addoption(
        "--purge_at_end",
        action="store_true",
        default=False,
        help="Purge account and user at end",
    )


@pytest.fixture(scope="class")
def api(pytestconfig):
    return pytestconfig.getoption("api")


@pytest.fixture(scope="class")
def email(pytestconfig):
    return pytestconfig.getoption("email")


@pytest.fixture(scope="class")
def account_id(pytestconfig):
    return pytestconfig.getoption("account_id")


@pytest.fixture(scope="class")
def password(pytestconfig):
    return pytestconfig.getoption("password")


class Keychain:
    def configure_keychain(self, *args, **kwargs):
        pass


@pytest.fixture(scope="class")
def manual(pytestconfig):
    return pytestconfig.getoption("manual")


@pytest.fixture(scope="class")
def purge_at_end(pytestconfig):
    return pytestconfig.getoption("purge_at_end")


@pytest.fixture(scope="function")
def pause_for_manual_action(pytestconfig):
    class suspend:
        def __init__(self):
            self.capture = pytestconfig.pluginmanager.getplugin("capturemanager")

        def __enter__(self):
            self.capture.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            self.capture.resume_global_capture()

    yield suspend()


@pytest.fixture(scope="class")
def existing_account(pytestconfig):
    if (account_id := pytestconfig.getoption("account_id")) and (
        password := pytestconfig.getoption("password")
    ):
        if not pytestconfig.getoption("email"):
            raise Exception(
                "Must provide email address when using --account_id and --password"
            )
        return dict(account_id=account_id, password=password)


@pytest.fixture(scope="class")
def setup_account(email, api, existing_account):
    account = _Account(account=None, handle=email, hq=api)
    iam = IAMAccountController(account)
    if existing_account:
        account.account = existing_account["account_id"]
        account.headers["account"] = existing_account["account_id"]
        account.password_login(existing_account["password"])
        account.headers["authorization"] = f"Bearer {account.token}"
        logging.info(f"[account_id: {existing_account['account_id']}]")
    else:
        res = iam.sign_up(company="pysdk-tests", email=email, name="Bob")
        password = "PySdkTests123!"
        account.headers["account"] = res["account_id"]
        account.password_login(res["temp_password"], password)
        account.account = res["account_id"]
        account.headers["authorization"] = f"Bearer {account.token}"
        logging.info(f'[account_id: {res["account_id"]}]')
        logging.info(
            f"--api '{api}' --email '{email}' --password '{password}' --account_id '{res['account_id']}'"
        )

    # service_user = unwrap(iam.create_service_user)(iam, name="pysdktests")
    # pytest.service_user_handle = service_user["handle"]
    # pytest.service_user_token = service_user["token"]
    expected_account = unwrap(iam.get_account)(iam)
    return account, expected_account


@pytest.fixture(scope="class")
def setup_existing_account(api, email, password, account_id):
    if not (api and account_id and email and password):
        raise Exception(
            "Expected existing account. Must specify api, account_id, email and password."
        )

    account = _Account(account=account_id, handle=email, hq=api)
    account.headers["account"] = account_id
    try:
        account.get_token()
    except Exception:
        account.password_login(password)
    account.headers["authorization"] = f"Bearer {account.get_token()}"
    logging.info(f"[account_id: {account_id}]")

    iam = IAMAccountController(account)
    expected_account = unwrap(iam.get_account)(iam)
    return account, expected_account


@pytest.fixture(scope="class")
def iam_account(setup_existing_account):
    account, _ = setup_existing_account
    return IAMAccountController(account)


@pytest.fixture(scope="class")
def iam_user(setup_existing_account):
    account, _ = setup_existing_account
    return IAMUserController(account)


@pytest.fixture(scope="class")
def build(setup_existing_account):
    account, _ = setup_existing_account
    return BuildController(account)


@pytest.fixture(scope="class")
def detect(setup_existing_account):
    account, _ = setup_existing_account
    return DetectController(account)


@pytest.fixture(scope="class")
def probe(setup_existing_account):
    account, _ = setup_existing_account
    return ProbeController(account)


@pytest.fixture(scope="class")
def partner(setup_existing_account):
    account, _ = setup_existing_account
    return PartnerController(account)


@pytest.fixture(scope="class")
def scm(setup_existing_account):
    account, _ = setup_existing_account
    return ScmController(account)


@pytest.fixture(scope="class")
def jobs(setup_existing_account):
    account, _ = setup_existing_account
    return JobsController(account)

@pytest.fixture(scope="class")
def export(setup_existing_account):
    account, _ = setup_existing_account
    return ExportController(account)


@pytest.fixture(scope="class")
def generate(setup_existing_account):
    account, _ = setup_existing_account
    return GenerateController(account)


@pytest.fixture(scope="class")
def my_test_id(my_test):
    return my_test["id"]


@pytest.fixture(scope="class")
def my_test(detect, account_id):
    test = next(
        (r for r in unwrap(detect.list_tests)(detect) if r["account_id"] == account_id),
        None,
    )
    logging.info(f"Test ID: {test['id']}")
    return test


@pytest.fixture(scope="class")
def my_threat_id(my_threat):
    return my_threat["id"]


@pytest.fixture(scope="class")
def my_threat(detect, account_id):
    threat = next(
        (
            r
            for r in unwrap(detect.list_threats)(detect)
            if r["account_id"] == account_id
        ),
        None,
    )
    logging.info(f"Threat ID: {threat['id']}")
    return threat


@pytest.fixture(scope="class")
def my_detection(detect, account_id):
    detection = next(
        (
            r
            for r in unwrap(detect.list_detections)(detect)
            if r["account_id"] == account_id
        ),
        None,
    )
    logging.info(f"Detection ID: {detection['id']}")
    return detection


@pytest.fixture(scope="class")
def my_threat_hunt_ids(detect, account_id):
    crwd, mde = None, None
    for threat_hunt in unwrap(detect.list_threat_hunts)(detect):
        if threat_hunt["account_id"] != account_id:
            continue
        if not crwd and threat_hunt["control"] == Control.CROWDSTRIKE.value:
            crwd = threat_hunt["id"]
        if not mde and threat_hunt["control"] == Control.DEFENDER.value:
            mde = threat_hunt["id"]
        if crwd and mde:
            break
    logging.info(f"CRWD Threat Hunt ID: {crwd}, MDE Threat Hunt ID: {mde}")
    return crwd, mde


@pytest.fixture(scope="class")
def service_user_token(iam_account):
    service_user = unwrap(iam_account.create_service_user)(
        iam_account, name="pysdktests"
    )
    return service_user["token"]
