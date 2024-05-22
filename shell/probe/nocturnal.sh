#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-east-2.s3.amazonaws.com}
vst=${PRELUDE_DIR:-.vst}
version='2.2'

echo "Prelude probe: version ${version}"

while :
do
    task=$(curl -sf --max-redirs 0 -H "token:${PRELUDE_TOKEN}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:${version}" https://api.preludesecurity.com)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')

    if [ "$uuid" ] && [ "$auth" = "$ca" ];then
        curl -sf --max-redirs 0 --create-dirs -o $vst/$uuid $task
        chmod +x $vst/$uuid && $vst/$uuid & test_pid=$!
        elapsed_time=0
        while kill -0 $test_pid 2> /dev/null; do
          if [ $elapsed_time -ge 45 ]; then
            kill -9 $test_pid 2> /dev/null
            echo "TIMEOUT: Killed long running test ${uuid}"
            code=102
          fi
          sleep 1
          elapsed_time=$((elapsed_time + 1))
        done
        if [[ $code -ne 102 ]]; then
          wait $test_pid
          code=$?
        fi
        dat="${uuid}:$([ -f $vst/$uuid ] && echo $code || echo 127)"
        unset code
    elif [ "$task" = "stop" ];then
        exit
    else
        rm -rf $vst
        unset dat
        sleep_sec=$(echo "$task" | grep -E '^[0-9]+$')
        sleep ${sleep_sec:-1800}
    fi
done
