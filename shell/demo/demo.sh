#!/bin/bash

GREEN=$(tput setaf 2)
RED=$(tput setaf 1)
YELLOW=$(tput setaf 3)
STANDOUT=$(tput bold)$(tput smul)
NC=$(tput sgr0)

PRELUDE_API=${PRELUDE_API:="https://api.preludesecurity.com"}
PRELUDE_TOKEN=$1
PRELUDE_DIR=${PRELUDE_DIR:=".vst"}
PROTECTED="0 9 15 100 104 105 106 107 126 127 137"

dos=$(uname -s)-$(uname -m)

declare -a tests=(
  '5ec67dd1-f6a3-4a5e-9d33-62bb64a339f0'    # LockBit Ransomware
)
declare -a names=(
  'LockBit Ransomware'
)
declare -a results

function check_relevance {
    echo -e "\n[ ] Conducting relevance test"
    sleep 1 && tput cuu 1 && tput el
    echo -e "${GREEN}[✓] Conducted relevance test: valid server or workstation detected${NC}"
}

function download_test {
    local _test_id=$1
    local _temp=$2
    echo -e "\n[ ] Downloading test"

    location=$(curl -sL -w %{url_effective} -o $_temp -H "token:${PRELUDE_TOKEN}" -H "dos:${dos}" -H "id:${_test_id}" -H "version:2.0" $PRELUDE_API)
    test=$(echo $location | grep -o '[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}' | head -n 1)
    sleep 1 && tput cuu 1 && tput el
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
    local _test_name=$2
    echo -e "\n[ ] Starting test"
    sleep 1 && tput cuu 1 && tput el
    $_temp
    local _res=$?
    if ( echo $PROTECTED | grep -w -q $_res );then
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
    rm -rf ${PRELUDE_DIR:?}/*
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
    curl -sfSL -H "token: ${PRELUDE_TOKEN}" -H "dos: ${dos}" -H "dat: ${_dat}" -H "version:2.0" $PRELUDE_API
}

function run_demo {
    local _test_id=${tests[$1]}
    local _test_name=${names[$1]}
    local _temp=$PRELUDE_DIR/$(uuidgen)
    echo -e "\n${STANDOUT}Test: ${_test_name}${NC}"
    echo -e "\nMore details at: https://www.preludesecurity.com/advisories/aa23-075a"
    sleep 1
    echo -e "\nStarting test at: $(date +"%T")"
    check_relevance
    download_test $_test_id $_temp
    execute_test $_temp "${_test_name}"
    local _res=$?
    execute_cleanup $_temp
    post_results $_test_id $_res
    if ( echo $PROTECTED | grep -w -q $_res );then
        results+=( "${GREEN}${_test_name}\tPROTECTED${NC}" )
    elif [ $_res -eq 101 ];then
        results+=( "${RED}${_test_name}\tUNPROTECTED${NC}" )
    else
        results+=( "${YELLOW}${_test_name}\tERROR${NC}" )
    fi
    echo -e "\n###########################################################################################################"
    sleep 3
}

mkdir -p $PRELUDE_DIR
trap 'rm -rf -- "$PRELUDE_DIR"' EXIT

for i in "${!tests[@]}"
do
	  run_demo "$i"
done

rm -rf $PRELUDE_DIR

echo -e "\n[*] Go to https://platform.preludesecurity.com to register for an account\n"
