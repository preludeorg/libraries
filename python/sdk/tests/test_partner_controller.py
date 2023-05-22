import pytest
from prelude_sdk.controllers.partner_controller import PartnerController


class TestPartnerController:

    def test_attach_partner(self, unwrap):
        """Test attach_partner method"""
        partner = PartnerController(pytest.account)
        res = unwrap(partner.attach)(partner, 'crowdstrike', 'https://api.us-2.crowdstrike.com', 'test', 'secret')
        assert not res['connected']

    def test_detach_partner(self, unwrap):
        """Test detach_partner method"""
        partner = PartnerController(pytest.account)
        unwrap(partner.detach)(partner, 'crowdstrike')
        assert True

