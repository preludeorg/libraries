#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-east-2.s3.amazonaws.com}
vst='.vst'

while :
do
    task=$(curl -sf -H "token:${PRELUDE_TOKEN}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:2" https://api.preludesecurity.com)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')

    if [ $uuid ] && [ $auth == $ca ];then
        curl -sf --create-dirs -o $vst/$uuid $task
        chmod +x $vst/$uuid && $vst/$uuid; code=$?
        dat="${uuid}:$([[ -f $vst/$uuid ]] && echo $code || echo 127)"
    elif [[ "$task" == "stop" ]];then
        exit
    else
        rm -rf $vst
        unset dat
        sleep 3600
    fi
done