#!/bin/bash

PRELUDE_API="https://detect.prelude.org"
PRELUDE_TOKEN=$1

confirm=true
pause=3

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

while :
do
    temp=$(mktemp)
    echo "[*] Contacting Prelude for next scheduled test"
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}')

    if [ -z "$test" ];then
        echo "[*] All scheduled tests are complete for today"
        sleep $pause
        read -p "[!] Would you like to install this script so it retests daily? (y/N) " -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]];then
            echo
            echo "[*] Downloading installation script"
            sleep $pause
            temp=$(mktemp)
            curl -sL -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API/download/install
            chmod +x $temp
            echo $'\e[1;33m'
            sudo $temp
            echo $'\e[0m'
        else
            echo
            echo "[*] No big deal. You can always do this later."
        fi
        sleep $pause
        echo "[*] Head back to your browser to analyze your results"
        echo "Goodbye!"
        break
    else
        echo -e "[*] Retrieved test with identifier: ${test}"
        sleep $pause
        echo -e "[*] Wrote test to temp file: ${temp}"
        sleep $pause
        ca=$(echo $location | sed -e 's|^[^/]*//||' -e 's|/.*$||')
        if [ "$confirm" = true ];then
            echo
            echo -e "> Tests are served from the Prelude Central Authority: ${ca}"
            echo -e "> This is one of several safety precautions built into test execution"
            echo -e "> Read the full safety report: https://docs.prelude.org/docs/safety"
            echo
            read -p "Press ENTER to run the test"
        fi
        chmod +x $temp
        echo "[*] Test written to disk successfully"
        sleep $pause
        echo "[*] Measuring the reaction from endpoint defense"
        sleep $pause

        if test -f "$temp";then
            echo "[!] Test was not quarantined. Moving on to execution."
            sleep $pause
            echo $'\e[1;33m'
            $temp
            res1=$?
            $temp -cleanup
            res2=$?
            echo $'\e[0m'
            max=$(( $res1 > $res2 ? $res1 : $res2 ))
        else
            max=9
        fi
        if [ "$confirm" = true ];then
            echo
            echo "> Prelude collects the minimal amount of telemetry for each test run"
            echo "> Only the test identifier and result code are sent off the endpoint"
            echo "> Results will display inside your Prelude Platform"
            echo
            read -p "Press ENTER to report this result"
        fi
        curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${test}:${max}" $PRELUDE_API
        echo -e "\n.........................\n"
        sleep $pause
        confirm=false
    fi
done