# Shell probes

Shell probes are intended to be dependency-free executable code that works on most common operating systems.

## Quick start

> [Register an endpoint](https://docs.preludesecurity.com/docs/probes#registering-endpoints) to get a token

### Raindrop 

Windows shell probe

```terminal
SETX PRELUDE_TOKEN <TOKEN> /M
.\raindrop.ps1
```

### Nocturnal

Mac / Linux shell probe

```terminal
export PRELUDE_TOKEN=<TOKEN>
./nocturnal.sh
```

### Vision

Docker shell probe

See: [../../container/dockerfile](../../container/dockerfile)