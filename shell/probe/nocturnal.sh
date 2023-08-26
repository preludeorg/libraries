#!/bin/sh

authority=${PRELUDE_CA:-prelude-account-us2-us-east-1.s3.amazonaws.com}

while :
do
    redirect=$(curl -sfL -w '%{url_effective}' -H "token:${PRELUDE_TOKEN}" -H "id:${1}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:2" https://api.us2.preludesecurity.com -o /dev/null)
    uuid=$(echo "$redirect" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    ca=$(echo "$redirect" | grep -oE '^[^/]*//[^/]*' | sed 's/^[^/]*\/\{2\}//')

    if [ $uuid ] && [ $ca == $authority ];then
        curl -sf --create-dirs -o $authority/$uuid $redirect
        chmod +x $authority/$uuid && $authority/$uuid
        code=$?
        dat="${uuid}:$([[ -f $authority/$uuid ]] && echo $code || echo 127)"
    elif [[ "$redirect" == *"stop"* ]];then
        exit
    else
        rm -rf $authority
        unset dat
        sleep 3600
    fi
done