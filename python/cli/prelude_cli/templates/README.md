# $NAME

This section should provide a description of the test, providing some background information (such as historical in-the-wild usage by threat actors or APTs), as well as briefly illustrating the test's intention, objective, and techniques utilized to achieve them. This section should NOT be too technical or overly long; a small paragraph should be sufficient.

## How

> Safety: This section should contain a kind of advisory statement which positively declares that the VST does not actually negatively affect the tested system in any way.

Steps:

1. This section enumerates the individual, atomic steps by which ...
2. ... the probe attempts to achieve the intended effect of the test ...
3. ... and thereby perform evaluation of any resident security solutions.

Example Output:
```bash
[$ID] Starting test at: $TIME
[$ID] Host is vulnerable, continuing with technique execution
[$ID] Completed with code: 101
[$ID] Ending test at: $TIME
```

## Resolution

If this test fails:

* Bulleted list of recommendations that the testing organization SHOULD consider ...
* ... based upon the nature of the test, as well as the point of failure.