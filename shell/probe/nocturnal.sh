#!/bin/bash

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
TEMPDIR=${TMPDIR:="/tmp"}

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

while :
do
    redirect=$(curl -sfS -w %{redirect_url} -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    test=$(echo $redirect | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    if [ ! -z "$test" ];then
        temp="${TEMPDIR}/detect"
        resp=$(curl -sfS -o $temp $redirect)
        if [ -f $temp ];then
            ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')
            if [ -z "$PRELUDE_CA" ] || [ "$PRELUDE_CA" == "$ca" ];then
                chmod +x $temp

                if test -f "$temp";then
                    $temp
                    dat="${test}:$?"
                    $temp -cleanup
                else
                    dat="${test}:9"
                fi
            fi

            rm -f $temp
            continue
        fi
    fi
    sleep 14400
done