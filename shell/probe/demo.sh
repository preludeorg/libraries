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
    echo
    echo "[*] Contacting Prelude for the next scheduled test"
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}')

    if [ -z "$test" ];then
        echo "[✓] All scheduled tests are complete for today"
        sleep $pause
        read -p "[!] Would you like to install this script so it retests daily? (Y/N) " -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]];then
            echo
            echo "[*] Downloading installation script"
            sleep $pause
            temp=$(mktemp)
            curl -sL -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API/download/install
            chmod +x $temp
            echo "[!] Installing software requires permission. You will be prompted for your password."
            echo
            echo "> The script is open source: https://github.com/preludeorg/libraries/blob/master/shell/install/install.sh"
            echo "> You will need to provide your account ID and account token, which you can export from Build"
            echo
            read -p "Press ENTER to continue"
            echo
            read -p "Enter your account ID: " ACCOUNT_ID
            read -p "Enter your account token: " ACCOUNT_TOKEN
            echo $'\e[1;33m'
            sudo $temp -a $ACCOUNT_ID -s $ACCOUNT_TOKEN
            echo $'\e[0m'
        else
            echo
            echo "[*] No big deal. You can always do this later."
        fi
        sleep $pause
        echo
        echo "See you back in the Prelude Platform!"
        echo
        break
    else
        echo -e "[✓] Retrieved test with identifier: ${test}"
        sleep $pause
        echo -e "[✓] Wrote test to temp file: ${temp}"
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
        echo
        echo "[*] Measuring the reaction from endpoint defense"
        chmod +x $temp
        sleep $pause

        if test -f "$temp";then
            echo "[!] Test was not quarantined. Moving on to execution."
            sleep $pause
            echo $'\e[1;33m'
            expect -c "set timeout 5; spawn $temp; expect timeout { exit 102 }"
            res1=$?
            expect -c "set timeout 5; spawn $temp -cleanup; expect timeout { exit 102 }"
            res2=$?
            echo $'\e[0m'
            max=$(( $res1 > $res2 ? $res1 : $res2 ))
        else
            max=9
        fi

        sleep $pause

        dat=${test}:${max}
        if [ "$confirm" = true ];then
            echo "> Prelude collects the minimal amount of telemetry from each test"
            echo "> Only the test identifier and result code are sent off the endpoint"
            echo "> Results will display inside your Prelude Platform"
            echo
            sleep $pause
            echo -e "[!] This test will send the following result: ${dat}"
            echo
            read -p "Press ENTER to continue"
        fi
        curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API
        sleep $pause
        confirm=false
    fi
done
