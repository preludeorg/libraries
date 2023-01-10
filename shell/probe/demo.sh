#!/bin/bash

GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

PRELUDE_API="https://api.preludesecurity.com"
PRELUDE_TOKEN=$1

sys=$(uname -s)-$(uname -m)
id="b74ad239-2ddd-4b1e-b608-8397a43c7c54"
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

function check_relevance {
    echo "This test is designed to be relevant for any workstation or server"
    echo
    echo -e "${GREEN}[✓] Result: The test is relevant for your machine${NC}"
}

function download_test {
    temp=$(mktemp)
    location=$(curl -sfSL -w %{url_effective} -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "id:${id}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    if [ -z "$test" ];then
        echo -e "${RED}[!] Failed to download test${NC}"
        exit 1
    else
        echo -e "${GREEN}[✓] Wrote to temporary file: ${temp}${NC}"
        chmod +x $temp
    fi
}

function execute_test {
    $temp
    test_result=$?
    echo
    echo -e "${GREEN}[✓] Test is complete${NC}"
}

function execute_cleanup {
    $temp -cleanup
    cleanup_result=$?
    echo
    echo -e "${GREEN}[✓] Clean up is complete${NC}"
}

function post_results {
    max=$(( $test_result > $cleanup_result ? $test_result : $cleanup_result ))
    dat=${test}:${max}
    curl -sfSL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API
    echo -e "${GREEN}[✓] Test result submitted${NC}"
}

function install_probe {
    echo "[+] Downloading installation script"
    temp=$(mktemp)
    curl -sfSL -o $temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" $PRELUDE_API/download/install
    test -s "$temp" || {
        echo -e "${RED}[!] Failed to download installation script${NC}"
        exit 1
    }
    chmod +x $temp
    echo
    read -p "Enter your Prelude Account ID: " ACCOUNT_ID
    read -p "Enter your Prelude Account token: " ACCOUNT_TOKEN
    sudo $temp -a $ACCOUNT_ID -s $ACCOUNT_TOKEN
}

echo
echo "###########################################################################################################"
echo
echo "Welcome to Prelude!"
echo
echo "Rule: Malicious files should quarantine when written to disk"
echo "Test: Will your computer quarantine a malicious Office document?"
echo
echo "Malicious files are used to gain entry and conduct cyberattacks against corporate systems through seemingly"
echo "innocuous email attachments or direct downloads. For example - a malicious macro was used by the BlueNoroff"
echo "group in a ransomware attack (Dec. 2022) [link]"
echo
echo "[+] CVE mappings: ABC, BCD, CDE, and XXX others [link]"
echo "[+] ATT&CK mappings: T1204.002"
echo
echo "###########################################################################################################"
echo
read -p "Press ENTER to continue"
echo
echo "Starting test at: $(date +"%T")"
echo
echo "-----------------------------------------------------------------------------------------------------------"
echo "[0] Conducting relevance test"
echo && sleep 3
check_relevance
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
    echo
    install_probe
fi
echo 
echo "###########################################################################################################"
echo
echo "###########################################################################################################"
echo
if [ "$test_result" = 100 ];then
    echo -e "${GREEN}[✓] Good job! Your computer detected and responded to a malicious Office document dropped on "
    echo -e "the disk${NC}"
else
    echo -e "${RED}[!] This test was able to verify the existence of this vulnerability on your machine, as well as drop"
    echo "a malicious Office document on the disk. If you have security controls in place that you suspect should"
    echo "have protected your host, you can use the artifacts above to try to understand why your defenses failed"
    echo -e "in your logs${NC}"
fi
echo
echo "[*] To view your results for this test and others, run additional tests, or learn about conducting continuous"
echo "security tests across your infrastructure, return to platform.preludesecurity.com"
echo
echo "###########################################################################################################"
echo
