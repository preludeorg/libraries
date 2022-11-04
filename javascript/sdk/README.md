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
