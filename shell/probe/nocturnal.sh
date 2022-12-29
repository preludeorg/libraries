#!/bin/bash

PRELUDE_API="https://detect.prelude.org"

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

while :
do
    temp=$(mktemp)
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}')

    if [ -z "$test" ];then
        sleep 43200
    else
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')
        if [ -z "$PRELUDE_CA" ] || ["$PRELUDE_CA" == "$ca"];then
            chmod +x $temp

            if test -f "$temp";then
                $temp
                res1=$?
                $temp -cleanup
                res2=$?
                max=$(( $res1 > $res2 ? $res1 : $res2 ))
            else
                max=9
            fi
            curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${test}:${max}" $PRELUDE_API
        fi
    fi
done