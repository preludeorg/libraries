#!/bin/bash

GREEN='\033[1;32m'
RED='\033[1;31m'
NC='\033[0m' # No Color

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_TOKEN=$1

sys=$(uname -s)-$(uname -m)
id="b74ad239-2ddd-4b1e-b608-8397a43c7c54"
dos=$(echo $sys | tr '[:upper:]' '[:lower:]')

function check_relevance {
    echo -e "${GREEN}[✓] Result: Success - server or workstation detected${NC}"
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
    if ( echo "100 9 17 18 105 127" | grep -w -q $test_result );then
        echo -e "${GREEN}[✓] Result: control test passed${NC}"
    elif [ $test_result -eq 101 ];then
        echo -e "${RED}[!] Result: control test failed${NC}"
    else
        echo -e "${RED}[!] An unexpected error occurred${NC}"
    fi
}

function execute_cleanup {
    $temp -cleanup
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
echo "Will your computer quarantine a malicious Office document?"
echo
echo "Malicious files are used to gain entry and conduct cyberattacks against corporate systems through seemingly"
echo "innocuous email attachments or direct downloads. For example - a malicious macro was used by the BlueNoroff"
echo "group in a ransomware attack (Dec. 2022)."
echo
echo "This test will attempt to download a malicious file to your disk (a macro enabled excel file generated with"
echo "Msfvenom) in order to see how your machine will respond. Since downloading malicious files increases your risk"
echo "by opening you up to further attack, the ability to detect and quarantine any potentially harmful files as"
echo "quickly as possible is an important part of maintaining a proper security posture."
echo
echo "This is a Verified Security Test (VST) Developed by Prelude Research Inc."
echo
echo "[+] Applicable CVE(s): CVE-2017-0199"
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
    echo -e "${GREEN}[✓] Good job! Your computer detected and responded to a malicious Office document dropped on "
    echo -e "the disk${NC}"
elif [ $test_result -eq 101 ];then
    echo -e "${RED}[!] This test was able to verify the existence of this vulnerability on your machine, as well as drop"
    echo "a malicious Office document on the disk. If you have security controls in place that you suspect should"
    echo -e "have protected your host, please review the logs${NC}"
else
    echo -e "${RED}[!] This test encountered an unexpected error during execution. Please try again${NC}"
fi
echo
echo "###########################################################################################################"
echo
echo "[*] Return to https://platform.preludesecurity.com to view your results"
echo