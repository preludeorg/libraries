#!/bin/sh

dos=$(uname -s)-$(uname -m)
dir=/opt/preludesecurity
mkdir -p "$dir"
pushd "$dir" &>/dev/null
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:${dos}" > "${dir}/nocturnal"
chmod +x "${dir}/nocturnal"
"${dir}/nocturnal" > "${dir}/detect.log" 2>&1 &
popd "$dir" &>/dev/null
exec /bin/sh -c "$*"