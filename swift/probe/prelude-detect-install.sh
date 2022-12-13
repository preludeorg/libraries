#!/usr/bin/env bash
# Defaults
account="2edd4c86b22a175af8d480904eaff647"
account_token="68e7cd07-2477-489d-885a-65576f3cbf6c"
ep_token=""
PRELUDE_HQ="https://detect.prelude.org"

# System vars
running_user="prelude"
primary_group="$(id -gn)"
agent_fname="moonlight"
app_wd="/opt/prelude"
app_dir="/opt/prelude/bin"
app_tmp="/tmp/prelude"
service_file_name="prelude-detect.service"
download_url="https://prelude-moonlight-download.s3.us-east-2.amazonaws.com/moonlight"

function usage {
    echo
    echo "Usage: $(basename $0) [-h] -e ENDPOINT_TOKEN [-q PRELUDE_HQ]" 2>&1
    echo
    echo '  -h                 Shows Usage'
    echo "  -e ENDPOINT_TOKEN  Account Token; Default: ${account_token}"
    echo "  -q PRELUDE_HQ      Headquarters server; Default: ${PRELUDE_HQ}"
    echo
    exit
}
optstring="e:q:h"
while getopts ${optstring} arg; do
    case ${arg} in
        e)
            account_token="${OPTARG}"
            ;;
        q)
            PRELUDE_HQ="${OPTARG}"
            ;;
        h)
            usage
            ;;
        ?)
            echo "Invalid option: -${OPTARG}."
            echo
            usage
            ;;
    esac
done

get_auth_app () {
    local _hq_host=$1
    local _account_token=$2

    echo "[+] Downloading Detect Endpoint..."
    local _agent_url="${download_url}_${CPUTYPE}"
    curl -s -X GET -L -H "token:${_account_token}" "${_agent_url}" > "${app_tmp}/${agent_fname}"

    test -r "${app_tmp}/${agent_fname}" || {
        echo "[!] Detect failed to download!" >&2
        exit 1
    }
}

get_endpoint_token() {
    local _hq_host=$1
    local _account_token=$2
    local _account=$3

    echo "[+] Provisioning Detect Endpoint Token..."
    local _token_url="${_hq_host}/account/endpoint"
    ep_token=$(curl -s -X POST -H "account:${_account}" -H "token:${_account_token}" -H "Content-Type: application/json" -d "{\"id\":\"${HOST}\",\"tag\":\"macOS\"}"  "${_token_url}")
    export ep_token
}

setup_persistence_macos () {
    local _plist_file_path=$1
    local _hq_host=$2
    local _ep_token=$3

    [[ ! -d "$(dirname $_plist_file_path)" ]] && mkdir "$(dirname $_plist_file_path)"

    echo "[+] Generate PLIST"
    cat << EOF | tee "${_plist_file_path}" >/dev/null
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>Prelude Detect</string>
        <key>UserName</key>
        <string>${running_user}</string>
        <key>EnvironmentVariables</key>
        <dict>
            <key>PRELUDE_HQ</key>
            <string>${_hq_host}</string>
            <key>PRELUDE_TOKEN</key>
            <string>${ep_token}</string>
        </dict>
        <key>ProgramArguments</key>
        <array>
            <string>${app_dir}/${agent_fname}</string>
        </array>
        <key>KeepAlive</key>
        <true/>
        <key>RunAtLoad</key>
        <true/>
        <key>StartInterval</key>
        <integer>30</integer>
    </dict>
</plist>
EOF
    launchctl unload -w "${_plist_file_path}" 2>/dev/null
    launchctl load -w "${_plist_file_path}"
}

# Main Application
echo "[+] Detect setup started"
# Check user input
if [[ -z $PRELUDE_HQ ]]
then
    # This should not fail unless the user provides a blank value
    echo "[!] Failed to provide endpoint, no headquarters server"
    usage
fi
if [[ -z $account_token ]]
then
    echo "[!] Failed to provide endpoint token"
    usage
fi

echo "[+] Determining OS"
# determine OS
os_type=""
if [[ ${OSTYPE} == "darwin"* ]]; then
    os_type="macos"
    # Setup OS vars
    running_user="${USER}"
    plist_path="/Users/${running_user}/Library/LaunchAgents/org.prelude.detect.plist"
    app_dir="/Users/${running_user}/.prelude/bin"
    app_tmp="${TMPDIR}/prelude"

else
    echo "[!] Unsupported OS!"
    exit 3
fi

if [[ $os_type == "macos" ]]; then
    mkdir -p "${app_tmp}"
    echo "[*] Standing up as user: ${running_user}"
    install -o "${running_user}" -g "${primary_group}" -m 750 -d "${app_dir}"

    # Do the setup
    get_auth_app "${PRELUDE_HQ}" "${account_token}"
    get_endpoint_token "${PRELUDE_HQ}" "${account_token}" "${account}"
    # Copy over the application
    install -o "${running_user}" -g "$primary_group" -m 755 "${app_tmp}/${agent_fname}" "${app_dir}/${agent_fname}"
    setup_persistence_macos "${plist_path}" "${PRELUDE_HQ}" "${ep_token}"
    unset ep_token

else
    echo "[!] OS type not yet supported!"
    exit 3
fi

echo "[*] Cleaning up tmp directory"
rm -rf "${app_tmp}"

echo "[=] Detect setup complete"

# EOF