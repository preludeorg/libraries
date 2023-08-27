#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-west-1.s3.amazonaws.com}

while :
do
    task=$(curl -sf -H "token:${PRELUDE_TOKEN}" -H "id:${uuid}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:2" https://api.preludesecurity.com)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')

    if [ $uuid ] && [ $auth == $ca ];then
        curl -sf --create-dirs -o $ca/$uuid $task
        chmod +x $ca/$uuid && $ca/$uuid; code=$?
        dat="${uuid}:$([[ -f $ca/$uuid ]] && echo $code || echo 127)"
        unset uuid
    elif [[ "$task" == "stop" ]];then
        exit
    else
        rm -rf $ca
        unset dat
        read -t 3600 uuid
    fi
done