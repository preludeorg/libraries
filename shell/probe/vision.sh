#!/bin/sh

dos=$(uname -s)-$(uname -m)
mkdir -p /opt/preludesecurity
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:${dos}" > /opt/preludesecurity/nocturnal
chmod +x /opt/preludesecurity/nocturnal
/opt/preludesecurity/nocturnal > /opt/preludesecurity/detect.log 2>&1 &

exec /bin/sh -c "$*"