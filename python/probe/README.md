# Presto

> One of Chopin's 24 Preludes. A virtuosic prelude, presents a technical challenge with its rapid hold-and-release of eighth notes against quarter notes in the right hand, involving chromatic movement.

# Usage

Install with:

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