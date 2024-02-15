To run all tests:
```pytest tests/ -v``` or ```pytest tests/ -vv```

To run all tests in one file:
```pytest tests/test_iam.py -v```

Some test files require set up from other files. Pick and choose tests to run with `-k`. Ex. run all the Partner tests:
```pytest tests/  -v -k "new_account or create_test or upload or get_test or register_endpoint or Partner"```

To see what will run (but not actually run the tests), use `--collect-only`:
```pytest tests/  -v -k "new_account or create_test or upload or get_test or register_endpoint or Partner" --collect-only```

When running the Partner tests locally, use `pytest-env` to pull env variables from a `pytest.ini` file:
```
pip install pytest-env
pytest tests/ -c tests/pytest.ini
```
My `pytest.ini` file looks like:
```
[pytest]
env =
    CROWDSTRIKE_API=blah
    CROWDSTRIKE_USER=blah
    CROWDSTRIKE_SECRET=blah

    DEFENDER_API=blah
    DEFENDER_USER=blah
    DEFENDER_SECRET=blah

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