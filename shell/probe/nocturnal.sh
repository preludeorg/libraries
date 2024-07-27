#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-east-2.s3.amazonaws.com}
vst=${PRELUDE_DIR:-.vst}
version='2.5'

echo "Prelude probe: version ${version}"

execute_test() {
    vst=$1
    uuid=$2
    task=$3
    echo "Executing test ${uuid}"
    curl -sf --max-redirs 0 --create-dirs -o $vst/$uuid $task
    chmod +x $vst/$uuid
    $vst/$uuid & test_pid=$!
    elapsed_time=0
    while kill -0 $test_pid 2> /dev/null; do
        if [ $elapsed_time -ge 45 ]; then
            disown $test_pid
            kill -9 $test_pid 2> /dev/null
            echo "TIMEOUT: Killed long running test ${uuid} (${test_pid})"
            code=102
        fi
        sleep 1
        elapsed_time=$((elapsed_time + 1))
    done
    if [ "$code" != "102" ]; then
        wait $test_pid
        code=$?
    fi
    echo "Test ${uuid} finished with code ${code}"
    return $([ -f $vst/$uuid ] && echo $code || echo 127)
}

while :
do
    body="{}"
    if [ "$collect_logs" = "1" ]; then
        body="{\"logs\":\"$(echo "$logs" | cut -c1-250000 | base64)\"}"
    fi
    response=$(curl -sf --max-redirs 0 -H "Content-Type: application/json" -H "token:${PRELUDE_TOKEN}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:${version}" -X POST --data ${body} https://api.preludesecurity.com)
    task=$(echo "$response" | head -n1)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')
    collect_logs=$(echo "$response" | sed -nE 's,collect_logs = (\d*),\1,p')

    if [ "$uuid" ] && [ "$auth" = "$ca" ];then
        logs=$(execute_test "$vst" "$uuid" "$task" 2>&1)
        code=$?
        dat="${uuid}:${code}"
        echo "${logs}"
    elif [ "$task" = "stop" ];then
        exit
    else
        rm -rf $vst
        unset dat
        sleep_sec=$(echo "$task" | grep -E '^[0-9]+$')
        sleep ${sleep_sec:-1800}
    fi
done
