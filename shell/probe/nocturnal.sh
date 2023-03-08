#!/bin/bash

PRELUDE_SLEEP=${PRELUDE_SLEEP:=14440}
PRELUDE_DIR=${PRELUDE_DIR:=".vst"}
PRELUDE_CA=${PRELUDE_CA:="prelude-account-prod-us-west-1.s3.amazonaws.com"}

api="https://api.preludesecurity.com"
dos=$(uname -s)-$(uname -m)

while :
do  
    exe=$PRELUDE_DIR/$(uuidgen)
    location=$(curl -sL -w %{url_effective} --create-dirs -o $exe -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $api)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)

    if [ $test ];then
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            echo "[P] Running $test as $exe"
            chmod +x $exe && $exe
            code=$?
            dat="${test}:$([[ -f $exe ]] && echo $code || echo 127)"
        else
            echo "[P] Bad authority: $ca" && exit 0
        fi
    else
        find $PRELUDE_DIR -type f -name "*" -mmin -5 -delete
        unset dat && sleep $PRELUDE_SLEEP
    fi
done