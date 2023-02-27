# Installer

Installers are intended to install probes as persistent services.

## Prerequisite

Create a SERVICE level user on your account. This type of account is restricted to endpoint registration so you do not need to treat the returned token as a password.

```prelude iam create-user <USERNAME> --permission SERVICE```

## Install

Download and run the installer, passing in your SERVICE credentials. This will install a probe as a persistent service.

```sudo -E ./install.sh -a <ACCOUNT_ID> -s <SERVICE_ACCOUNT_TOKEN>```

By default, Nocturnal will install on [Linux/Mac](https://github.com/preludeorg/libraries/blob/master/shell/probe/nocturnal.sh) endpoints and [Raindrop](https://github.com/preludeorg/libraries/blob/master/shell/probe/raindrop.ps1) on Windows. If you want to install a different probe, select one from the [probe compatibility](https://github.com/preludeorg/libraries#probe-compatibility) table and pass the probe name into the installer with the -n argument.