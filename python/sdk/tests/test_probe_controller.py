import os
import pytest

from prelude_sdk.controllers.probe_controller import ProbeController


@pytest.mark.order(after='test_iam_controller.py::TestIAMController::test_new_account')
class TestProbeController:

    def test_download(self, unwrap):
        """Test download method"""
        probe = ProbeController(pytest.account)
        probe_name = 'nocturnal'
        res = probe.download(name=probe_name, dos='linux-amd64')
        assert res is not None
        with open(f'{probe_name}.sh', 'w') as f:
            f.write(res)
        assert os.path.isfile(f'{probe_name}.sh')
        pytest.probe = os.path.abspath(f'{probe_name}.sh')
        os.chmod(pytest.probe, 0o755)
