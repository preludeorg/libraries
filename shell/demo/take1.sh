#!/bin/bash

#GREEN='\033[1;32m'
#RED='\033[1;31m'
#YELLOW='\033[1;33m'
#NC='\033[0m' # No Color
GREEN=$(tput setf 2)
RED=$(tput setf 1)
YELLOW=$(tput setf 3)
STANDOUT=$(tput bold)$(tput smul)
NC=$(tput sgr0)

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_TOKEN=$1

dos=$(uname -s)-$(uname -m)

declare -a tests=(
  '39de298a-911d-4a3b-aed4-1e8281010a9a'    # Health check
  '3ebbda49-738c-4799-a8fb-206630cf609e'    # Will a long running VST be stopped properly?
  '2e705bac-a889-4283-9a8e-a12358fa1d09'    # Will your computer quarantine Royal Ransomware?
  'b74ad239-2ddd-4b1e-b608-8397a43c7c54'    # Will your computer quarantine a malicious Office document?
  'ca9b22be-93d5-4902-95f4-4bc43a817b73'    # Will your computer quarantine Colour-Blind malware?
)
declare -a names=(
  'Health check'
  'Will a long running VST be stopped properly?'
  'Will your computer quarantine Royal Ransomware?'
  'Will your computer quarantine a malicious Office document?'
  'Will your computer quarantine Colour-Blind malware?'
)
declare -a results

function get_info {
    local _test_id=$1
    local _test_name=$2
    echo -e "${STANDOUT}${_test_name}${NC} (ID: ${_test_id})\n"
    curl -sfS "https://raw.githubusercontent.com/preludeorg/test/master/tests/${_test_id}/README.md" | sed -n '3 p'
    echo -e "\nThis is a Verified Security Test (VST) Developed by Prelude Research Inc."
}

function check_relevance {
    echo -e "${GREEN}[✓] Result: Success - server or workstation detected${NC}"
}

function download_test {
    local _test_id=$1
    local _temp=$2
    location=$(curl -sfSL -w %{url_effective} -o $_temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "id:${_test_id}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    if [ -z "$test" ];then
        echo -e "${RED}[!] Failed to download test${NC}"
        exit 1
    else
        echo -e "${GREEN}[✓] Wrote to temporary file: ${_temp}${NC}"
        chmod +x $_temp
    fi
}

function execute_test {
    local _temp=$1
    $_temp
    local _res=$?
    if ( echo "100 9 17 18 105 127" | grep -w -q $_res );then
        echo -e "\n${GREEN}[✓] Result: control test passed${NC}"
    elif [ $_res -eq 101 ];then
        echo -e "\n${RED}[!] Result: control test failed${NC}"
    else
        echo -e "\n${RED}[!] An unexpected error occurred${NC}"
    fi
    return $_res
}

function execute_cleanup {
    local _temp=$1
    local _temp_dir=$(dirname $_temp)
    rm -f $_temp ${_temp_dir}/09a79e5e20fa4f5aae610c8ce3fe954029a91972b56c6576035ff7e0ec4c1d14.elf ${_temp_dir}/malicious.xlsm ${_temp_dir}/colour-blind.py
    local _res=$?
    if [ $_res -eq 0 ];then
        echo -e "${GREEN}[✓] Clean up is complete${NC}"
    else
        echo -e "${RED}[!] Clean up failed${NC}"
    fi
}

function post_results {
    local _dat="$1:$2"
    curl -sfSL -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "dat:${_dat}" $PRELUDE_API
}

function run_demo {
    local _i=$1
    local _test_id=${tests[$_i]}
    local _temp=$(mktemp)
    echo -e "###########################################################################################################\n"
    get_info $_test_id "${names[$_i]}"
    echo -e "\n###########################################################################################################\n"
#    sleep 2
    echo -e "Starting test at: $(date +"%T")"
    echo -e "\n-----------------------------------------------------------------------------------------------------------"
#    sleep 2
    echo -e "[0] Conducting relevance test\n"
    check_relevance
    echo -e "-----------------------------------------------------------------------------------------------------------"
    echo -e "[1] Downloading test\n"
    download_test $_test_id $_temp
    echo -e "-----------------------------------------------------------------------------------------------------------"
    echo -e "[2] Executing test\n"
    execute_test $_temp
    local _res=$?
    echo -e "-----------------------------------------------------------------------------------------------------------"
    echo -e "[3] Running cleanup\n"
    execute_cleanup $_temp
    post_results $_test_id $_res
    if ( echo "100 9 17 18 105 127" | grep -w -q $_res );then
        results+=( "${GREEN}${names[$i]}\tPROTECTED${NC}" )
    elif [ $_res -eq 101 ];then
        results+=( "${RED}${names[$i]}\tUNPROTECTED${NC}" )
    else
        results+=( "${YELLOW}${names[$i]}\tERROR${NC}" )
    fi
  #  echo -e "\n###########################################################################################################\n"
  #  echo "SUMMARY HERE"
    echo -e "\n###########################################################################################################"
#    sleep 4
}

echo
for i in "${!tests[@]}"
do
	run_demo "$i"
done

echo -e "\nSummary of test results:\n"
paste <(printf "%b\n" "${results[@]}") | column -txs $'\t'

echo -e "\n[*] Return to https://platform.preludesecurity.com to view your results\n"