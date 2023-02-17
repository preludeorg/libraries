#!/bin/bash

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

while :
do
    temp=$(mktemp)
    output=$(curl -sfSL -w "%{http_code}%{url_effective}" -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    if ( echo "401 403" | grep -w -q ${output:0:3} );then
      sleep 86400
      continue
    fi
    test=$(echo ${output:3} | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ -z "$test" ];then
        sleep 14400
    else
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
    fi
done