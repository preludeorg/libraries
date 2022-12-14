# Prelude Libraries

Prelude maintains a collection of open-source libraries that interact with our products, [Build](https://docs.prelude.org/docs/build) and [Detect](https://docs.prelude.org/docs/the-basics).

Libraries are organized by language and categorized by:

* Probe
* SDK

> Additionally, the Prelude CLI supports all Build and Detect functionality. Install from source or through ```pip install prelude-cli```.

## Probe

A probe is an ephemeral endpoint process that requires no special privileges and no installation. Probes have one duty: accept security tests from Detect, execute them, and respond with the result. [Read the docs](https://docs.prelude.org/docs/probes).

## SDK

A Software Development Kit (SDK) allows you to build your own tooling against the Prelude Service API. 
