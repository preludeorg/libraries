#!/bin/sh

mkdir -p /opt/preludesecurity
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:linux-amd64" > /opt/preludesecurity/nocturnal
chmod +x /opt/preludesecurity/nocturnal
/opt/preludesecurity/nocturnal > /opt/preludesecurity/detect.log 2>&1 &

exec /bin/sh -c "$*"