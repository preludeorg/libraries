#!/bin/bash

PRELUDE_CA="prelude-account-us1-us-west-1.s3.amazonaws.com"
PRELUDE_DIR=".vst"

api="https://api.preludesecurity.com"
dos=$(uname -s)-$(uname -m)

while :
do
    redirect=$(curl -sfL -w '%{url_effective}' -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" -H "version:1.2" $api -o /dev/null)
    test=$(echo "$redirect" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')

    if [ $test ];then
        ca=$(echo $redirect | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            curl -sf --create-dirs -o $PRELUDE_DIR/$test $redirect
            chmod +x $PRELUDE_DIR/$test && $PRELUDE_DIR/$test
            code=$?
            dat="${test}:$([[ -f $PRELUDE_DIR/$test ]] && echo $code || echo 127)"
        fi
    elif [[ "$redirect" == *"upgrade"* ]];then
        sleep 30 && exit
    else
        rm -rf $PRELUDE_DIR
        unset dat
        sleep 3600
    fi
done
