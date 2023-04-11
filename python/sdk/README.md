# Prelude SDK

Interact with the Prelude Service API via Python. 

> The prelude-cli utility wraps around this SDK to provide a rich command line experience.

Install this package to write your own tooling that works with Build or Detect functionality.

- IAM: manage your account
- Build: write and maintain your collection of security tests
- Detect: schedule security tests for your endpoints

## Quick start

```bash
pip install prelude-sdk
```

## Documentation 

TBD

## Testing

To test the Python SDK and Probes, run the following commands from the python/sdk/ directory:

```bash
pip install -r tests/requirements.txt
pytest tests --api https://api.preludesecurity.com --email <EMAIL>
```