#!/bin/bash

PRELUDE_DIR=".vst"
PRELUDE_CA="prelude-account-us1-us-west-1.s3.amazonaws.com"

api="https://api.preludesecurity.com"
dos=$(uname -s)-$(uname -m)

while :
do
    location=$(curl -sfL -w %{url_effective} --create-dirs -o $PRELUDE_DIR/0 -H "token: ${PRELUDE_TOKEN}" -H "dos: ${dos}" -H "dat: ${dat}" -H "version: 1.1" $api)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ $test ];then
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            echo "[P] Running $test"
            mv $PRELUDE_DIR/0 $PRELUDE_DIR/$test
            chmod +x $exe && $PRELUDE_DIR/$test
            code=$?
            dat="${test}:$([[ -f $PRELUDE_DIR/$test ]] && echo $code || echo 127)"
        fi
    elif [[ "$location" == *"upgrade"* ]];then
        echo "[P] Upgrade required" && exit 1
    else
        rm -r $PRELUDE_DIR
        unset dat
        sleep 14440
    fi
done
