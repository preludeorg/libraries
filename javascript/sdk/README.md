# Prelude SDK

Use this utility if you want direct access to the Prelude API.

## Install

```bash
npm install @theprelude/sdk
```

## Quick start

The following example registers an account and gets the tests:

```typescript
import * as Prelude from "@theprelude/sdk";
const service = new Prelude.Service({ host: "https://detect.prelude.org" });

const credentials = await service.iam.newAccount("user_handle");

service.setCredentials(credentials);

const tests = await service.build.listTests();
```

## End-to-End tests

The following steps with outline how to run the end to end tests for the Prelude Service API.
These tests aim to call all public/authenticated endpoints in the system and verfied the results.

### How to run

1. Change to the `javascript/sdk` directory

2. [Optional] Set the environment to run tests against
   > By default this is set to https://detect.dev.prelude.org.

```bash
export VITE_PRELUDE_SERVICE_URL="<url here>"
```

3. Install dependencies

```bash
yarn install
```

4. Run the test command

```bash
yarn test e2e
```

#### Test UI

The test suite can also open a UI to show tests as they run. Open it by running

```bash
yarn test:ui e2e
```

#### Filter Tests

Run a subset of the tests by specifing the part after `e2e/`.

```bash
yarn test e2e/iam
yarn test e2e/build
yarn test e2e/detect
```
