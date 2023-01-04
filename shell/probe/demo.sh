#!/bin/bash

PRELUDE_API="https://api.staging.preludesecurity.com"
PRELUDE_TOKEN=$1

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

function download_test {
    temp=$(mktemp)
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}')
    if [ -z "$test" ];then
        echo -e "[!] No test found for the '${dos}' architecture"
        exit 1
    else
        echo -e "[✓] Downloaded into temporary file: ${temp}"
        chmod +x $temp
    fi
}

function execute_test {
    $temp
    test_result=$?
    echo "[✓] Test is complete"
}

function execute_cleanup {
    $temp -cleanup
    cleanup_result=$?
    echo "[✓] Clean up is complete"
}

function post_results {
    dat=${test}:${test_result}
    curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API
    echo "[✓] Test result saved"
}

function install_probe {
    echo "[+] Downloading installation script"
    temp=$(mktemp)
    curl -sL -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API/download/install
    chmod +x $temp
    read -p "Enter your Prelude Account ID: " ACCOUNT_ID
    read -p "Enter your Prelude Account token: " ACCOUNT_TOKEN
    sudo $temp -a $ACCOUNT_ID -s $ACCOUNT_TOKEN
}

echo
echo "###########################################################################################################"
echo
echo "Rule #1: Will your computer quarantine a malicious Office document?"
echo 
echo "[*] There have been 1,501 CVE numbers tied to malicious Office documents"
echo "[*] MITRE ATT&CK classifies a malicious Office macro as T1015"
echo "[*] A malicious macro was the root of the recent Blah ransomware attack"
echo
echo "###########################################################################################################"
echo
echo "Starting test at: $(date +"%T")"
echo
echo "-----------------------------------------------------------------------------------------------------------"
echo "[1] Downloading test"
echo
download_test
echo "-----------------------------------------------------------------------------------------------------------"
echo "[2] Executing test"
echo
execute_test
echo "-----------------------------------------------------------------------------------------------------------"
echo "[3] Running cleanup"
echo
execute_cleanup
echo "-----------------------------------------------------------------------------------------------------------"
echo "[4] Saving results"
echo
post_results
echo "-----------------------------------------------------------------------------------------------------------"
read -p "[Optional] Would you like to install this test so it runs daily? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]];then
    install_probe
fi
echo 
echo
echo
echo "###########################################################################################################"
echo
echo "Summary"
echo 
if [ "$test_result" = 100 ];then
    echo "[✓] Good job! Your computer detected and responded to a malicious Office document dropped on the disk."
else
    echo "[!] Your computer was unable to detect a malicious Office document dropped on the disk."
    echo "[!] This puts the machine at risk from a variety of computer attacks, including many tied to CVE exploits such as blah."
    echo "[!] We advise you reach out to support@prelude.org for help selecting an appropriate endpoint defense."
fi
echo
echo "[*] Learn about more tests you can run: https://docs.prelude.org/docs/rules"
echo
echo "###########################################################################################################"
echo
