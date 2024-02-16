Requires: Python3.11

To run all tests:
```
pytest tests/ -v
pytest tests/ -vv
```

To run all tests in one file:
```
pytest tests/test_iam.py -v
```

Some test files require set up from other files. Pick and choose tests to run with `-k`. Ex. run all the Partner tests:
```
pytest tests/ -v -k "new_account or create_test or upload or get_test or register_endpoint or Partner"
```

To see what will run (but not actually run the tests), use `--collect-only`:
```
pytest tests/ -v -k "new_account or create_test or upload or get_test or register_endpoint or Partner" --collect-only
```

When running the Partner tests locally, use `pytest-env` to pull env variables from a `pytest.ini` file:
```
pip install pytest-env
pytest tests/ -c pytest.ini
```
Add `--rootdir` if `pytest.ini` is in a different location, for aesthetics:
```
pytest python/sdk/tests -vv -c ../my-prelude/pytest.ini --email mahina@preludesecurity.com --rootdir python/sdk
```
My `pytest.ini` file looks like:
```
[pytest]
env =
    CROWDSTRIKE_HOST=blah
    CROWDSTRIKE_EDR_ID=blah
    CROWDSTRIKE_OS=blah
    CROWDSTRIKE_PLATFORM=blah
    CROWDSTRIKE_POLICY=blah
    CROWDSTRIKE_POLICY_NAME=blah
    CROWDSTRIKE_API=blah
    CROWDSTRIKE_USER=blah
    CROWDSTRIKE_SECRET=blah

    DEFENDER_HOST=blah
    DEFENDER_EDR_ID=blah
    DEFENDER_OS=blah
    DEFENDER_PLATFORM=blah
    DEFENDER_API=blah
    DEFENDER_USER=blah
    DEFENDER_SECRET=blah

    S1_HOST=blah
    S1_EDR_ID=blah
    S1_OS=blah
    S1_PLATFORM=blah
    S1_POLICY=blah
    S1_POLICY_NAME=blah
    S1_API=blah
    S1_USER=blah
    S1_SECRET=blah

    SPLUNK_API=blah
    SPLUNK_SECRET=blah

    VECTR_API=blah
    VECTR_USER=blah
    VECTR_SECRET=blah

    S3_BUCKET=blah
```