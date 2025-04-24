#!/bin/sh

ca=${PRELUDE_CA:-prelude-account-us1-us-east-2.s3.amazonaws.com}
vst=${PRELUDE_DIR:-"$PWD/.vst"}
envTimeout=${PRELUDE_MAXTIMEOUT-45}
if ! [[ "$envTimeout" =~ ^[0-9]+$ ]]; then
  envTimeout=45
fi
timeout=$(( envTimeout < 45 ? 45 : envTimeout ))

version='2.8'

echo "Prelude probe: version ${version}"


while :
do
    task=$(curl -sf --max-redirs 0 -H "token:${PRELUDE_TOKEN}" -H "dos:$(uname -s)-$(uname -m)" -H "dat:${dat}" -H "version:${version}" https://api.preludesecurity.com)
    uuid=$(echo "$task" | sed -nE 's/.*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*/\1/p')
    auth=$(echo "$task" | sed -nE 's,^[^/]*//([^/]*)/.*,\1,p')

    if [ "$uuid" ] && [ "$auth" = "$ca" ];then
        echo "Downloading $uuid"
        curl -sf --max-redirs 0 --create-dirs -o "$vst/$uuid" $task
        chmod +x "$vst/$uuid"
        echo "Invoking $uuid"
        cd "$vst" || exit 1
        ./"$uuid" & test_pid=$!
        elapsed_time=0
        while kill -0 $test_pid 2> /dev/null; do
          if [ $elapsed_time -ge $timeout ]; then
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
        dat="${uuid}:$([ -f "$vst/$uuid" ] && echo $code || echo 127)"
        echo "Done Invoking $dat"
        unset code
    elif [ "$task" = "stop" ];then
        exit
    else
        echo "Test cycle done"
        rm -rf "$vst"
        unset dat
        sleep_sec=$(echo "$task" | grep -E '^[0-9]+$')
        sleep ${sleep_sec:-1800}
    fi
done
