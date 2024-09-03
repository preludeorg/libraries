#!/bin/sh

dos=$(uname -s)-$(uname -m)
dir=/opt/preludesecurity
mkdir -p "$dir"
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:${dos}" > "${dir}/nocturnal"
chmod +x "${dir}/nocturnal"
"${dir}/nocturnal" > "${dir}/detect.log" 2>&1 &
exec /bin/sh -c "$*"
