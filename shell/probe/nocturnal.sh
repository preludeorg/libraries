#!/bin/bash

PRELUDE_CA="prelude-account-us1-us-west-1.s3.amazonaws.com"

api="https://api.preludesecurity.com"
dos=$(uname -s)-$(uname -m)

while :
do
    redirect=$(curl -sfL -w '%{url_effective}' -H "token: ${PRELUDE_TOKEN}" -H "dos: ${dos}" -H "dat: ${dat}" -H "version: 1.2" $api -o /dev/null)
    test=$(echo $redirect | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ $test ];then
        ca=$(echo $redirect | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            curl -sf --create-dirs -o .vst/$test $redirect
            chmod +x .vst/$test && .vst/$test
            code=$?
            dat="${test}:$([[ -f .vst/$test ]] && echo $code || echo 127)"
        fi
    elif [[ "$redirect" == *"upgrade"* ]];then
        echo "[P] Upgrade required" && exit 1
    else
        rm -rf .vst
        unset dat
        sleep 14440
    fi
done
