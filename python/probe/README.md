# Presto

A probe written in Python. 

Presto can run as either a standalone script or be installed into another application as a library (SDK). 

## Quick start: Standalone

```bash
export PRELUDE_TOKEN=<YOUR TOKEN>
python detect_probe/presto.py
```

## Quick start: SDK

Install the library via pip:
```bash
pip install detect-probe
```

Include presto in a project with:

```python
from detect_probe.service import ProbeService

service = ProbeService(account_id='<ACCOUNT_ID>', secret='<ACCOUNT_TOKEN>')
token = service.register()
service.start(token=token)
```
