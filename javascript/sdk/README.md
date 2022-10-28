# Prelude SDK

Use this utility if you want direct access to the Prelude API.

## Install

```bash
npm install @prelude/sdk
```

## Quick start

The following example registers an account and gets the manifest:

```typescript
import * as Prelude from "@prelude/sdk";
const service = new Prelude.Service({ host: "https://detect.prelude.org" });

const credentials = await service.iam.newAccount("test@example.com");

service.setCredentials(credentials);

const manifest = await service.build.listManifest();
```
