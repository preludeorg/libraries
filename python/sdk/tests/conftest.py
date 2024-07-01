import pytest
import uuid

from prelude_sdk.controllers.build_controller import BuildController
from prelude_sdk.controllers.iam_controller import IAMController


@pytest.fixture(scope='session')
def unwrap():
    def unwrapper(func):
        if not hasattr(func, '__wrapped__'):
            return func
        return unwrapper(func.__wrapped__)
    yield unwrapper


@pytest.fixture(scope='session')
def pause_for_manual_action(pytestconfig):
    class suspend:
        def __init__(self):
            self.capture = pytestconfig.pluginmanager.getplugin('capturemanager')

        def __enter__(self):
            self.capture.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            self.capture.resume_global_capture()

    yield suspend()


def pytest_addoption(parser):
    parser.addoption('--api', default='https://api.us2.preludesecurity.com', action='store', help='API target for tests')
    parser.addoption('--email', default='test@auto-accept.developer.preludesecurity.com', action='store', help='Email address to use for testing')
    parser.addoption('--account_id', action='store', help='Account ID to use for testing')
    parser.addoption('--token', action='store', help='Token to use for testing. Only used in conjunction with --account_id')


@pytest.fixture(scope='session')
def api(pytestconfig):
    return pytestconfig.getoption('api')


@pytest.fixture(scope='session')
def email(pytestconfig):
    return pytestconfig.getoption('email')


class Account:
    def __init__(self, account_id='', token='', hq=''):
        self.hq = hq
        self.profile = 'test'
        self.headers = dict(
            account=account_id,
            token=token,
            _product='py-sdk'
        )

    def read_keychain_config(self):
        return {self.profile: dict()}

    def write_keychain_config(self, cfg):
        pass


@pytest.fixture(scope='session')
def existing_account(pytestconfig):
    if (account_id := pytestconfig.getoption('account_id')) and (token := pytestconfig.getoption('token')):
        return dict(account_id=account_id, token=token)


@pytest.fixture(scope='session')
def manual(pytestconfig):
    return not pytestconfig.getoption('email').endswith('@auto-accept.developer.preludesecurity.com')


@pytest.fixture(scope='session')
def setup_account(unwrap, manual, pause_for_manual_action, email, api, existing_account):
    if hasattr(pytest, 'expected_account'):
        return

    pytest.account = Account(hq=api)
    iam = IAMController(pytest.account)
    if existing_account:
        pytest.account.headers['account'] = existing_account['account_id']
        pytest.account.headers['token'] = existing_account['token']
        print(f'[account_id: {existing_account["account_id"]}]', end=' ')
        pytest.expected_account = unwrap(iam.get_account)(iam)
        return

    res = unwrap(iam.new_account)(iam, company='pysdk-tests', user_email=email, user_name='Bob')
    if manual:
        with pause_for_manual_action:
            input("Press ENTER to continue testing after verifying the account...\n")

    pytest.account.headers['account'] = res['account_id']
    pytest.account.headers['token'] = res['token']
    print(f'[account_id: {res["account_id"]}]', end=' ')
    pytest.expected_account = unwrap(iam.get_account)(iam)


@pytest.fixture(scope='session')
def setup_test(unwrap):
    if hasattr(pytest, 'expected_test'):
        return
    
    build = BuildController(pytest.account)
    pytest.test_id = str(uuid.uuid4())
    pytest.expected_test = unwrap(build.create_test)(build, test_id=pytest.test_id, name='test_name', unit='custom', technique=None)


@pytest.fixture(scope='session')
def setup_threat(unwrap):
    if hasattr(pytest, 'expected_threat'):
        return
    
    build = BuildController(pytest.account)
    pytest.threat_id = str(uuid.uuid4())
    tests = ['881f9052-fb52-4daf-9ad2-0a7ad9615baf', 'b74ad239-2ddd-4b1e-b608-8397a43c7c54', pytest.test_id]
    pytest.expected_threat = unwrap(build.create_threat)(build,
                                                         name='threat_name',
                                                         published='2023-11-13',
                                                         threat_id=pytest.threat_id,
                                                         source_id='aa23-061a',
                                                         source='https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-061a',
                                                         tests=','.join(tests))


@pytest.fixture(scope='session')
def setup_detection(unwrap):
    if not pytest.expected_account['features']['detections']:
        return
    if hasattr(pytest, 'expected_detection'):
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

    pytest.expected_detection = unwrap(build.create_detection)(build, rule=pytest.detection_rule, test_id=pytest.test_id, detection_id=pytest.detection_id, rule_id=str(uuid.uuid4()))


@pytest.fixture(scope='session')
def setup_threat_hunt(unwrap):
    if not pytest.expected_account['features']['threat_intel']:
        return
    if hasattr(pytest, 'expected_threat_hunt'):
        return

    build = BuildController(pytest.account)
    pytest.threat_hunt_id = str(uuid.uuid4())
    pytest.expected_threat_hunt = unwrap(build.create_threat_hunt)(
        build,
        test_id=pytest.test_id,
        name='test threat hunt',
        query='test query',
        threat_hunt_id=pytest.threat_hunt_id)
