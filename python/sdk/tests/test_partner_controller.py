import pytest
from prelude_sdk.controllers.partner_controller import PartnerController


class TestPartnerController:

    def test_attach_partner(self, unwrap):
        """Test attach_partner method"""
        try:
            partner = PartnerController(pytest.account)
            unwrap(partner.attach)(partner, 'crowdstrike', 'https://api.us-2.crowdstrike.com', 'test', 'secret')
        except Exception as e:
            assert 'Authentication failed with crowdstrike' in str(e)

    def test_detach_partner(self, unwrap):
        """Test detach_partner method"""
        try:
            partner = PartnerController(pytest.account)
            unwrap(partner.detach)(partner, 'crowdstrike')
        except Exception as e:
            assert 'No partner by that name' in str(e)
