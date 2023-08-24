#!/bin/bash

PRELUDE_DIR=".vst"
PRELUDE_CA="prelude-account-us2-us-east-1.s3.amazonaws.com"

api="https://api.us2.preludesecurity.com"
dos=$(uname -s)-$(uname -m)

while :
do
    redirect=$(curl -sfL -w '%{url_effective}' -H "token: ${PRELUDE_TOKEN}" -H "dos: ${dos}" -H "id:b74ad239-2ddd-4b1e-b608-8397a43c7c54" -H "dat: ${dat}" -H "version: 1.2" $api -o /dev/null)
    test=$(echo $redirect | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ $test ];then
        ca=$(echo $redirect | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            curl -sf --create-dirs -o "$PRELUDE_DIR/$test" $redirect
            chmod +x $PRELUDE_DIR/$test && $PRELUDE_DIR/$test
            code=$?
            dat="${test}:$([[ -f $PRELUDE_DIR/$test ]] && echo $code || echo 127)"
        fi
    elif [[ "$location" == *"upgrade"* ]];then
        echo "[P] Upgrade required" && exit 1
    else
        rm -rf $PRELUDE_DIR
        unset dat
        sleep 14440
    fi
done
