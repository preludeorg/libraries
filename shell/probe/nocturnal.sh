#!/bin/bash

PRELUDE_SLEEP=${PRELUDE_SLEEP:=14440}
PRELUDE_DIR=${PRELUDE_DIR:="./cache"}
PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_CA=${PRELUDE_CA:="prelude-account-prod-us-west-1.s3.amazonaws.com"}

dos=$(echo $(uname -s)-$(uname -m))

while :
do  
    exe=$PRELUDE_DIR/$(uuidgen)
    location=$(curl -sL -w %{url_effective} --create-dirs -o $exe -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)    
    unset dat

    if [ $test ];then
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ "$PRELUDE_CA" == "$ca" ];then
            echo "[P] Running $test masquerading as $exe"
            chmod +x $exe
            $exe
            dat="${test}:$?"
        else
            echo "[P] Authority mismatch: $exe" && exit 0
        fi
    else
        find $PRELUDE_DIR -type f -name "*" -mmin -5 -delete
        sleep $PRELUDE_SLEEP
    fi
done