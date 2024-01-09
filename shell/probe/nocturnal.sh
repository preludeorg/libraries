#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-east-2.s3.amazonaws.com}
vst='.vst'

while :
do
    task=$(curl -sf -H "token:${PRELUDE_TOKEN}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:2" https://api.preludesecurity.com)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')

    if [ "$uuid" ] && [ "$auth" = "$ca" ];then
        curl -sf --create-dirs -o $vst/$uuid $task
        chmod +x $vst/$uuid && $vst/$uuid; code=$?
        dat="${uuid}:$([ -f $vst/$uuid ] && echo $code || echo 127)"
    elif [ "$task" = "stop" ];then
        exit
    else
        rm -rf $vst
        unset dat

        # Option 1. Explicitly check that sleep is an int. Otherwise default to 1800s
        sleep_sec=$(echo "$task" | grep -E '^[0-9]+$')
        sleep ${sleep_sec:-1800}

        # Option 2. try/catch method. I couldn't find a way to do sneaky bash injection, and this might is probably slightly more efficient
        sleep $task 2>/dev/null || (echo "Invalid sleep time: $task" && sleep 1800)
    fi
done
