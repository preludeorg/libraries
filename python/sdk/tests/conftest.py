import pytest


@pytest.fixture
def unwrap():
    def unwrapper(func):
        if not hasattr(func, '__wrapped__'):
            return func

        return unwrapper(func.__wrapped__)

    yield unwrapper


@pytest.fixture
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
    parser.addoption("--api", default='https://api.us2.preludesecurity.com', action='store', help='API target for tests')
    parser.addoption('--email', default='test@auto-accept.developer.preludesecurity.com', action='store', help='Email address to use for testing')


@pytest.fixture(scope='session')
def api(pytestconfig):
    return pytestconfig.getoption('api')


@pytest.fixture(scope='session')
def email(pytestconfig):
    return pytestconfig.getoption('email')
