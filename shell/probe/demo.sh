#!/bin/bash

PRELUDE_API="https://api.staging.preludesecurity.com"
PRELUDE_TOKEN=$1

sys=$(uname -s)-$(uname -m)
id="b74ad239-2ddd-4b1e-b608-8397a43c7c54"
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

function download_test {
    temp=$(mktemp)
    location=$(curl -sL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}')
    if [ -z "$test" ];then
        echo -e "[!] No test found for the '${dos}' architecture"
        exit 1
    else
        echo -e "[✓] Wrote to temporary file: ${temp}"
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
    curl -sL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" -H "id:${id}" $PRELUDE_API
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
echo "Will your computer quarantine a malicious Office document?"
echo
echo "[*] There have been 1,798 CVE numbers tied to malicious Office documents"
echo "[*] MITRE ATT&CK classifies a malicious Office macro as technique T1204.002"
echo "[*] A malicious macro was used by the BlueNoroff group in a ransomware attack (Dec. 2022)"
echo
echo "###########################################################################################################"
echo
read -p "Press ENTER to continue"
echo
echo "Starting test at: $(date +"%T")"
echo
echo "-----------------------------------------------------------------------------------------------------------"
echo "[1] Downloading test"
echo
download_test
echo "-----------------------------------------------------------------------------------------------------------"
echo "[2] Executing test"
echo && sleep 3
execute_test
echo "-----------------------------------------------------------------------------------------------------------"
echo "[3] Running cleanup"
echo && sleep 3
execute_cleanup
echo "-----------------------------------------------------------------------------------------------------------"
echo "[4] Saving results"
echo && sleep 3
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
if [ "$test_result" = 100 ];then
    echo "[✓] Good job! Your computer detected and responded to a malicious Office document dropped on the disk."
else
    echo "[!] Your computer was unable to detect a malicious Office document dropped on the disk."
    echo "[!] Reach out to support@prelude.org for help selecting an appropriate endpoint defense."
fi
echo
echo "[*] Learn about more tests you can run: https://docs.prelude.org/docs/rules"
echo
echo "###########################################################################################################"
echo
