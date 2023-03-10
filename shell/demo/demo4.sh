#!/bin/bash

GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_TOKEN=$1

sys=$(uname -s)-$(uname -m)
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

test_id="74077d3b-6a2f-49fa-903e-99cad6f34cf6"
test_intro=$'Will your computer quarantine a malicious mach-o file?

Malicious files are used to gain entry and conduct cyberattacks against corporate systems through seemingly
innocuous email attachments or direct downloads. For example - a malicious Mac mach-o file was used by Earth Berberoka
during an attack in April 2022.

This test will attempt to download a defanged malicious file to your disk - containing a signature for the oRAT malware used by Earth Berberoka - to see how your endpoint defenses will respond. 
Downloading malicious files can open you up to further attacks, so the ability to quickly detect and quarantine any potentially harmful files is an important part of maintaining a proper security posture.

This is a Verified Security Test (VST) Developed by Prelude Research Inc.

[+] Applicable CVE(s): CVE-2022-42821
[+] ATT&CK mappings: T1573'
test_success=$'Your computer detected and responded to a malicious mach-o file dropped on
the disk${NC}'
test_failure=$'This test was able to verify the existence of this vulnerability on your machine, as well as drop
a malicious mach-o file on the disk. If you have security controls in place that you suspect should have protected your host, 
please review the please review the logs${NC}'

function check_relevance {
    echo -e "${GREEN}[✓] Result: Success - server or workstation detected${NC}"
}

function find_test {
    redirect=$(curl -sfS -w %{redirect_url} -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "id:${test_id}" $PRELUDE_API)
    test=$(echo $redirect | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    if [ -z "$test" ];then
        echo -e "${RED}[!] Failed to find test${NC}"
        exit 1
    fi
}

function download_test {
    temp=$(mktemp)
    resp=$(curl -w %{http_code} -sfS -o $temp $redirect)
    if [ $resp -ne 200 ];then
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
    if ( echo "100 9 17 18 105 127" | grep -w -q $test_result );then
        echo -e "${GREEN}[✓] Result: control test passed${NC}"
    elif [ $test_result -eq 101 ];then
        echo -e "${RED}[!] Result: control test failed${NC}"
    else
        echo -e "${RED}[!] An unexpected error occurred${NC}"
    fi
}

function execute_cleanup {
    rm -rf ./o.RAT
    cleanup_result=$?
    echo
    if [ $cleanup_result -eq 100 ];then
        echo -e "${GREEN}[✓] Clean up is complete${NC}"
    else
        echo -e "${RED}[!] Clean up failed${NC}"
    fi
}

function post_results {
    dat=${test}:${test_result}
    curl -sfSL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${dat}" $PRELUDE_API
}

echo
echo "###########################################################################################################"
echo
echo "$test_intro"
echo
echo "###########################################################################################################"
echo
find_test
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
if ( echo "100 9 17 18 105 127" | grep -w -q $test_result );then
    echo
    echo -e "${GREEN}[✓] Clean up is complete${NC}"
else
    execute_cleanup
fi
post_results
echo
echo "###########################################################################################################"
echo
if ( echo "100 9 17 18 105 127" | grep -w -q $test_result );then
    echo -e "${GREEN}[✓] Good job! "${test_success}""
elif [ $test_result -eq 101 ];then
    echo -e "${RED}[!] "${test_failure}""
else
    echo -e "${RED}[!] This test encountered an unexpected error during execution. Please try again${NC}"
fi
echo
echo "###########################################################################################################"
echo
echo "[*] Return to https://platform.preludesecurity.com to view your results"
echo
