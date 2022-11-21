## Prelude Libraries

Prelude maintains a collection of open-source libraries that are used to power our products:


<ol>
          <li><a href="https://www.preludesecurity.com/products/operator">Prelude Operator</a>: Perform realistic security assessments on security systems</li>
          <li><a href="https://www.preludesecurity.com/products/build">Prelude Build</a>: Security test authoring</li>
          <li><a href="https://www.preludesecurity.com/products/detect">Prelude Detect</a>: Continuous security testing</li>
</ol>


These libraries are designed for security engineers, DevOps engineers, software engineers and IT analysts. They allow you to download, use and edit Prelude's core services in whatever format you're most comfortable with. 

<h3>Libraries</h3>

| Library Name  | Purpose       | Repository 
| ------------- | ------------- | -------------
| Go Probe  | A standalone SDK probe that supports Go  | <a href="https://github.com/preludeorg/libraries/tree/master/go/probe">go/probe</a>
| Javascript SDK  | Direct access to the Prelude API  | <a href="https://github.com/preludeorg/libraries/tree/master/go/probe">javascript/sdk</a>
| Python CLI  | Access Prelude Build & Detect through a CLI  | <a href="https://github.com/preludeorg/libraries/tree/master/python/cli">python/cli</a>
| Python Probe  | A standalone SDK probe that supports Python  | <a href="https://github.com/preludeorg/libraries/tree/master/python/probe">python/probe</a>
| Python SDK  | Direct access to the Prelude API  | <a href="https://github.com/preludeorg/libraries/tree/master/python/sdk">python/sdk</a>
| Shell Install | Copy installation scripts  | <a href="https://github.com/preludeorg/libraries/tree/master/shell/install">shell/install</a>
| Swift Probe  | Standalone probe for Linux & Mac  | <a href="https://github.com/preludeorg/libraries/tree/master/swift/probe">swift/probe</a>


<h3>The Probe</h3>

A probe is a temporary process that requires no special privileges and no installation to run. A probe can just be started. Probes are designed to be very lightweight - measuring between 1-50KB on disk - and to run anywhere you have code. As such, probes can deploy out on devices ranging from laptops to servers to cloud environments and OT infrastructure. Probes are designed to work with <a href="https://www.preludesecurity.com/products/detect">Prelude Detect</a>, bringing safety and scale to continuous testing.</a>

<h4>Standalone probes</h4>

Deploying a standalone probe requires you to:

Set a PRELUDE_TOKEN environment variable, with the value equal to your endpoint token.
Download the probe binary on the endpoint
This bash script demonstrates both.

          PRELUDE_TOKEN='<INSERT TOKEN>'
          curl -X GET -L "https://detect.prelude.org/download/moonlight?os=darwin" -H "token:${PRELUDE_TOKEN}") > moonlight
          chmod +x moonlight
          ./moonlight
