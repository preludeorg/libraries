# Probe SDK

Use this utility if you want direct access to the Prelude API.

> The detect-cli utility wraps around this SDK to provide a rich command line experience.

## Modules

This SDK allows you to interact with several Prelude modules:

* Accounts (AccountController)
* Endpoints (EndpointController)
* Database (DatabaseController)
* Schedule (ScheduleController)

## Install

```bash
pip install detect-sdk
```

## Quick start

The following example adds a new user to your account:

```python
from detect_sdk.controllers.account_controller import AccountController
from detect_sdk.models.account import Account
from detect_sdk.models.codes import Permission


controller = AccountController(account=Account())
token = controller.create_user(permission=Permission['SERVICE'].value)
```