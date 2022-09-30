# Probe SDK

If you need access to the mHQ service beyond just launching a probe, this SDK is available for use.

## Modules

This SDK allows you to interact with several different mHQ services:

* Accounts (AccountController)
* Endpoints (EndpointsController)
* Probes (ProbeController)
* TTPs (TTPsController)

Similar to the AWS Boto3 library, this is essentially just a wrapper around common API calls to our services.


# Usage

Install with:

```bash
pip install detect-sdk
```

Then use it with:

```python
from detect_sdk.controllers.account_controller import AccountController
from detect_sdk.models.account import Account
from detect_sdk.models.codes import Permission


controller = AccountController(account=Account())
token = controller.create_user(permission=Permission['SERVICE'].value)
```