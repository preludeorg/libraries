#!/bin/bash

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

while :
do
    location=$(curl -sL -w %{url_effective} -o "detect-vst" -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ -z "$test" ];then
        sleep 14400
    else
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')
        if [ -z "$PRELUDE_CA" ] || ["$PRELUDE_CA" == "$ca"];then
            chmod +x $temp

            if test -f "$temp";then
                $temp
                res=$?
                $temp -cleanup
            else
                res=9
            fi
            curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${test}:${res}" $PRELUDE_API
        fi
    fi
    rm -f $temp
done
