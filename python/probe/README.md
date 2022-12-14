# Presto

A probe written in Python. 

Presto can run as either a standalone script or be installed into another app as a library (SDK). 

## Quick start | Standalone

> [Register an endpoint](https://docs.prelude.org/docs/probes#registering-endpoints) to get a token

```bash
export PRELUDE_TOKEN=<YOUR TOKEN>
python detect_probe/presto.py
```

## Quick start | SDK

Install the library:
```bash
pip3 install detect-probe
```

Include presto in a project:

```python
from detect_probe.service import ProbeService

service = ProbeService(account_id='<ACCOUNT_ID>', secret='<ACCOUNT_TOKEN>')
token = service.register()
service.start(token=token)
```
