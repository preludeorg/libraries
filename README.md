## Prelude Libraries

Prelude maintains a collection of open-source libraries that are used to power our products:

* [Prelude Build](https://www.preludesecurity.com/products/build): Security test authoring
* [Prelude Detect](https://www.preludesecurity.com/products/detect): Continuous security testing

<h3>Libraries</h3>

| Library Name  | Purpose       | Repository 
| ------------- | ------------- | -------------
| Go Probe  | An SDK probe that supports Go  | <a href="https://github.com/preludeorg/libraries/tree/master/go/probe">go/probe</a>
| Python Probe  | An SDK probe that supports Python  | <a href="https://github.com/preludeorg/libraries/tree/master/python/probe">python/probe</a>
| Swift Probe  | Standalone probe for Linux & Mac  | <a href="https://github.com/preludeorg/libraries/tree/master/swift/probe">swift/probe</a>
| PowerShell Probe  | Standalone probe Windows  | <a href="https://github.com/preludeorg/libraries/tree/master/powershell/probe">powershell/probe</a>
| Javascript SDK  | Direct access to the Prelude API  | <a href="https://github.com/preludeorg/libraries/tree/master/go/probe">javascript/sdk</a>
| Python SDK  | Direct access to the Prelude API  | <a href="https://github.com/preludeorg/libraries/tree/master/python/sdk">python/sdk</a>
| Python CLI  | Access Prelude Build & Detect through a CLI  | <a href="https://github.com/preludeorg/libraries/tree/master/python/cli">python/cli</a>
| Shell Install | Standalone probe installation guides  | <a href="https://github.com/preludeorg/libraries/tree/master/shell/install">shell/install</a>


<h3>The Probe</h3>

A probe is a temporary process that requires no special privileges and no installation to run. A probe can just be started. Probes are designed to be very lightweight - measuring between 1-50KB on disk - and to run anywhere you have code. As such, probes can deploy out on devices ranging from laptops to servers to cloud environments and OT infrastructure. Probes are designed to work with <a href="https://www.preludesecurity.com/products/detect">Prelude Detect</a>, bringing safety and scale to continuous testing.</a>

Probes can be installed either standalone or imported into an existing project via a library (SDK). In either case, when the probe starts, it will periodically run security tests against the device it's installed on. [Read the full documentation](https://docs.prelude.org/docs/probes).
