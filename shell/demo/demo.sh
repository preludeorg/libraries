#!/bin/bash

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
STANDOUT=$(tput bold)$(tput smul)
NC=$(tput sgr0)

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_TOKEN=$1
PRELUDE_DIR=${PRELUDE_DIR:=".vst"}

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

function check_relevance {
    echo -e "\n[ ] Conducting relevance test"
    sleep 1 && tput cuu 1 && tput el
    echo -e "${GREEN}[✓] Conducted relevance test: Success - server or workstation detected${NC}"
}

function download_test {
    local _test_id=$1
    local _temp=$2
    echo -e "\n[ ] Downloading test"

    location=$(curl -sfSL -w %{url_effective} -o $_temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "id:${_test_id}" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    tput cuu 1 && tput el
    if [ -z "$test" ];then
        echo -e "${RED}[!] Failed to download test${NC}"
        exit 1
    else
        echo -e "${GREEN}[✓] Downloaded test to temporary file: ${_temp}${NC}"
        chmod +x $_temp
    fi
}

function execute_test {
    local _temp=$1
    echo -e "\n[ ] Executing test"
    sleep 1 && tput cuu 1 && tput el
    $_temp
    local _res=$?
    if ( echo "100 9 17 18 105 127" | grep -w -q $_res );then
        echo -e "${GREEN}[✓] Executed test: control test passed${NC}"
    elif [ $_res -eq 101 ];then
        echo -e "${RED}[!] Executed test: control test failed${NC}"
    else
        echo -e "${YELLOW}[!] Executed test: an unexpected error occurred${NC}"
    fi
    return $_res
}

function execute_cleanup {
    echo -e "\n[ ] Running cleanup"
    rm -rf $PRELUDE_DIR/*
    local _res=$?
    tput cuu 1 && tput el
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
    local _temp=$PRELUDE_DIR/$(uuidgen)
    echo -e "\n${STANDOUT}Test: ${names[$_i]}${NC}"
    echo -e "\nMore details at: https://github.com/preludeorg/test/tree/master/tests/${_test_id}"
    sleep 1
    echo -e "\nStarting test at: $(date +"%T")"
    check_relevance
    download_test $_test_id $_temp
    execute_test $_temp
    local _res=$?
    execute_cleanup $_temp
    post_results $_test_id $_res
    if ( echo "100 9 17 18 105 127" | grep -w -q $_res );then
        results+=( "${GREEN}${names[$i]}\tPROTECTED${NC}" )
    elif [ $_res -eq 101 ];then
        results+=( "${RED}${names[$i]}\tUNPROTECTED${NC}" )
    else
        results+=( "${YELLOW}${names[$i]}\tERROR${NC}" )
    fi
    echo -e "\n###########################################################################################################"
    sleep 3
}

mkdir -p $PRELUDE_DIR

for i in "${!tests[@]}"
do
	  run_demo "$i"
done

rm -rf $PRELUDE_DIR

echo -e "###########################################################################################################"
echo -e "\nSummary of test results:\n"
paste <(printf "%b\n" "${results[@]}") | column -txs $'\t'

echo -e "\n[*] Return to https://platform.preludesecurity.com to view your results\n"