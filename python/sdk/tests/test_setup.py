import pytest


@pytest.mark.setup
@pytest.mark.order(1)
class TestSetup:

    def test_setup_account(self, setup_account):
        setup_account
        assert True
