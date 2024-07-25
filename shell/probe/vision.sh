#!/bin/sh

dos=$(uname -s)-$(uname -m)
dir=/opt/preludesecurity
mkdir -p "${dir}/.vst"
curl -sL "https://api.preludesecurity.com/download/nocturnal" -H "dos:${dos}" > "${dir}/nocturnal"
chmod +x "${dir}/nocturnal"
cd "${dir}/.vst" &>/dev/null
"${dir}/nocturnal" > "${dir}/detect.log" 2>&1 &
exec /bin/sh -c "$*"