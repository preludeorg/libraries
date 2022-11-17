import os
import getpass
import platform
import subprocess
import sys
from urllib import request


from detect_probe.service import ProbeService


def download_probe(token, target, dos=f'{platform.system()}-{platform.machine()}'.lower(), name='moonlight'):
    try:
        r = request.Request(
            url=f'https://detect.prelude.org/download/{name}',
            headers={
                'token': token,
                'dos': dos
            })
        with request.urlopen(r) as rs:
            result = rs.read()
            with open(target, 'wb') as fp:
                fp.write(result)
    except Exception as e:
        print(e)
        exit(1)


def darwin(current_user, token, probe_name='moonlight'):
    from plistlib import dump, loads
    probe_path = f'/Users/{current_user}/.prelude/bin/{probe_name}'
    os.makedirs(f'/Users/{current_user}/.prelude/bin/', exist_ok=True)
    download_probe(token=token, target=probe_path)
    plist_path = f'/Users/{current_user}/Library/LaunchAgents/org.prelude.detect.plist'
    plist = loads(f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>Prelude Detect</string>
        <key>UserName</key>
        <string>{current_user}</string>
        <key>EnvironmentVariables</key>
        <dict>
            <key>PRELUDE_TOKEN</key>
            <string>{token}</string>
        </dict>
        <key>ProgramArguments</key>
        <array>
            <string>{probe_path}</string>
        </array>
        <key>KeepAlive</key>
        <true/>
        <key>RunAtLoad</key>
        <true/>
        <key>StartInterval</key>
        <integer>30</integer>
    </dict>
</plist>""".encode('utf-8'))
    with open(plist_path, 'wb') as fp:
        dump(plist, fp)
    subprocess.run(f'launchctl unload -w "{plist_path}" 2>/dev/null', shell=True)
    subprocess.run(f'launchctl load -w "{plist_path}"', shell=True)


if __name__ == '__main__':
    probe_svc = ProbeService(account_id=os.getenv('PRELUDE_ACCOUNT_ID'), secret=os.getenv('PRELUDE_ACCOUNT_SECRET'))
    if sys.platform.startswith('darwin'):
        if token := probe_svc.register():
            darwin(current_user=getpass.getuser(), token=token)
        else:
            print('Failed to register endpoint')
    elif sys.platform.startswith('linux'):
        if token := probe_svc.register():
            darwin(current_user=getpass.getuser(), token=token)
        else:
            print('Failed to register endpoint')
    else:
        print('Unsupported OS')
