[CmdletBinding()]
param(
  [Parameter(HelpMessage="Prelude Account Id")]
  [String]$preludeAccountId="db78df67c1891444da7cd4a1f6402d77",
  [Parameter(HelpMessage="Prelude Account Secret")]
  [String]$preludeAccountSecret="7ee12efd-e770-4e5c-8c8d-3c5dac4c9e68",
  [Parameter(HelpMessage="Probe name")]
  [String]$probeName="raindrop",
  [Parameter(HelpMessage="Endpoint tags (as a comma-separated string")]
  [String]$endpointTags=""
)

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "User")
    if ($envVal) { return $envVal } else { return $default }
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$PRELUDE_API = FromEnv "PRELUDE_API" "https://api.preludesecurity.com"

function LogError {
    param([string]$errStr)
    Write-Host "[!] $errStr" -ForegroundColor Red
}

function LogMessage {
    param([string]$str)
    Write-Host "[+] $str"
}

function RegisterEndpoint {
    LogMessage "Provisioning Detect Endpoint Token..."
    $data = @{"id"= "$($env:computername):$(New-Guid)";"tags"=$endpointTags} | ConvertTo-Json
    $response = Invoke-WebRequest -Method POST -Uri $PRELUDE_API/detect/endpoint -UseBasicParsing -Headers @{"account"=$preludeAccountId;"token"=$preludeAccountSecret} -ContentType "application/json" -Body $data
    if($response.StatusCode -ne 200) {
        LogError "Endpoint failed to register! $($response.StatusDescription)"
        Exit 1
    }
    return $response.Content
}

function DownloadProbe {
    param ([string]$token, [string]$dos, [string]$out)
    LogMessage "Downloading Probe..."
    try {
        [void](Invoke-WebRequest -Method GET -Uri $PRELUDE_API/download/$probeName -UseBasicParsing -Headers @{"token"=$token;"dos"=$dos} -OutFile $out -PassThru)
    } catch [System.Net.WebException] {
        LogError "Detect failed to download! $($_.ErrorDetails)"
        Exit 1
    }
}

function StartTask {
    param([string]$token, [string]$wd, [string]$location)
    LogMessage "Creating task"
    $id = "prelude-detect"
    $name = "Prelude Detect"

    Stop-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue -Confirm:$false

    $action = New-ScheduledTaskAction -Id $id -Execute "powershell.exe" -Argument "-File $($location)" -WorkingDirectory $wd
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $principal = New-ScheduledTaskPrincipal -LogonType S4U -UserId "$env:UserDomain\$env:UserName"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DontStopOnIdleEnd -ExecutionTimeLimit '00:00:00'
    $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal
    [void](Register-ScheduledTask -TaskName $name -InputObject $task)
    [void](Start-ScheduledTask -TaskName $name -AsJob)
    LogMessage "Task started"
}

LogMessage "Detect setup started"
$parentDir=Join-Path ([System.Environment]::ExpandEnvironmentVariables("%LOCALAPPDATA%")) "prelude"
$probePath=($parentDir | Join-Path -ChildPath $probeName) + ".ps1"
if(Test-Path -path $probePath -PathType Leaf) {
    Remove-Item $probePath
}
[void](New-Item -Path $parentDir -ItemType Directory -Force)
LogMessage "Determining OS"
$dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE
$token=RegisterEndpoint
[Environment]::SetEnvironmentVariable("PRELUDE_TOKEN", $token, "User")
[Environment]::SetEnvironmentVariable("PRELUDE_API", $PRELUDE_API, "User")
DownloadProbe $token $dos $probePath
StartTask $token $parentDir $probePath
Write-Host "[=] Detect setup complete"
