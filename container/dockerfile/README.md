# Dockerfile & Entrypoint.sh Guide

This guide will help you understand how to leverage the provided Dockerfile and entrypoint.sh in your own Docker projects.

## Files

The project contains the following files:

- `Dockerfile`: This file is used by Docker to build an image.
- `entrypoint.sh`: Thisx script is executed when a container is run from the Docker image.

## Dockerfile

```Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt install curl -y
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
```

This Dockerfile does the following:

1. Starts with the latest Ubuntu image.
2. Updates the package lists and installs curl.
3. Copies the entrypoint.sh script from your project into the root directory of the image.
4. Gives execute permissions to the entrypoint.sh file.
5. Sets entrypoint.sh as the script to be run when a container is started from the image.
6. Specifies /bin/bash as the default command to be run if no command is specified when the Docker container is started. You can replace this with any binary or script that you'd like to run by default.

## Entrypoint.sh

```bash
#!/bin/sh

mkdir -p /opt/preludesecurity
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:linux-amd64" > /opt/preludesecurity/nocturnal
chmod +x /opt/preludesecurity/nocturnal
/opt/preludesecurity/nocturnal > /opt/preludesecurity/detect.log 2>&1 &

exec /bin/sh -c "$*"
```

This script does the following:

1. Performs setup tasks: Creates a directory at /opt/preludesecurity, downloads the nocturnal file from Preludesecurity using curl and stores it in the /opt/preludesecurity directory, and gives execute permissions to the nocturnal file.
2. Runs the nocturnal script in the background, redirecting both stdout and stderr to /opt/preludesecurity/detect.log.
3. Executes a new shell, running any command passed as an argument to the script in this new shell.

## Usage

To use these files in your project:

1. Ensure both Dockerfile and entrypoint.sh are in your project directory.
2. Make sure the entrypoint.sh file is executable (`chmod +x entrypoint.sh`).
3. Build the Docker image by running `docker build -t my-image .` from the project directory.
4. Run a container from your image with `docker run -it my-image`.

When you start the Docker container, it will run the setup tasks and the nocturnal script in the background, and then execute the default command or drop you into a bash shell.

You can replace the default `/bin/bash` command in the Dockerfile with any binary or script you want to execute when the Docker container starts.

---

Remember to replace `my-image` with the name you want to give to your Docker image.