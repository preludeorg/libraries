#!/bin/sh

authority=${PRELUDE_CA:-prelude-account-us2-us-east-1.s3.amazonaws.com}

while :
do
    response=$(curl -sfi -H "token:${PRELUDE_TOKEN}" -H "id:${1}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:1" https://api.us2.preludesecurity.com)
    test=$(echo "$response" | grep -o 'https://[^[:space:]]*')
    uuid=$(echo "$test" | awk -F '/' '{print $(NF-1)}')
    ca=$(echo "$test" | awk -F '/' '{print $3}')

    if [ $uuid ] && [ $ca == $authority ];then
        curl -sf --create-dirs -o $authority/$uuid $test
        chmod +x $authority/$uuid && $authority/$uuid
        code=$?
        dat="${uuid}:$([[ -f $authority/$uuid ]] && echo $code || echo 127)"
    elif [[ "$test" == *"stop"* ]];then
        exit
    else
        rm -rf $authority
        unset dat
        sleep 3600
    fi
done