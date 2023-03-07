#!/bin/bash

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_DIR=${PRELUDE_DIR:="./cache"}
PRELUDE_SLEEP=${PRELUDE_SLEEP:=14440}

dos=$(echo $(uname -s)-$(uname -m))

while :
do  
    exe=$PRELUDE_DIR/$(uuidgen)
    location=$(curl -sL -w %{url_effective} --create-dirs -o $exe -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)    

    if [ $test ];then
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')

        if [ -z "$PRELUDE_CA" ] || [ "$PRELUDE_CA" == "$ca" ];then
            if test -f $exe;then
                echo "[P] Running $test masquerading as $exe"
                chmod +x $exe
                $exe
            fi
            dat="${test}:$?"
        fi
    else
        echo "[P] Cleaning up temporary cache"
        find $PRELUDE_DIR -type f -name "*" -mmin -1 -delete
        sleep $PRELUDE_SLEEP
    fi
done