#!/bin/sh

dos=$(uname -s)-$(uname -m)
dir=/opt/preludesecurity
curl -sf --max-redirs 0 --create-dirs -o "${dir}/nocturnal" -H "dos:${dos}" "https://api.preludesecurity.com/download/nocturnal"
chmod +x "${dir}/nocturnal"
"${dir}/nocturnal" &
exec /bin/sh -c "$*"
