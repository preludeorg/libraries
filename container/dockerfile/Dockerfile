FROM ubuntu:latest
RUN apt-get update && apt install curl -y
RUN curl -sL "https://api.preludesecurity.com/download/vision" -H "dos:linux-x86_64" -o /vision
RUN chmod +x /vision
ENTRYPOINT ["/vision"]
CMD ["/bin/bash"]
