# Dockerfile Guide

This guide will help you understand how to leverage the provided Dockerfile in your own Docker projects.

## Dockerfile

```Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt install curl -y
RUN curl -sL "https://api.preludesecurity.com/download/vision" -H "dos:linux-x86_64" -o /vision
RUN chmod +x /vision
ENTRYPOINT ["/vision"]
CMD ["/bin/bash"]
```

This Dockerfile does the following:

1. Starts with the latest Ubuntu image.
2. Updates the package lists and installs curl.
3. Curls the vision script into the root directory of the image.
4. Gives execute permissions to the vision file.
5. Sets vision as the script to be run when a container is started from the image.
6. Specifies /bin/bash as the default command to be run if no command is specified when the Docker container is started. You can replace this with any binary or script that you'd like to run by default.

## Usage

To use these files in your project:

1. Ensure both Dockerfile is your project directory. 
2. Build the Docker image by running `docker build -t my-image .` from the project directory. 
3. Run a container from your image with `docker run -e PRELUDE_TOKEN='51a585060b99c5a9db6c9b00e11632c9' -it my-image`.

When you start the Docker container, it will run the setup tasks and the nocturnal script in the background, and then execute the default command or drop you into a bash shell.

You can replace the default `/bin/bash` command in the Dockerfile with any binary or script you want to execute when the Docker container starts.

---

Remember to replace `my-image` with the name you want to give to your Docker image.
