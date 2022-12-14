[CmdletBinding()]
param(
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Id")]
  [String]$preludeAccountId,
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Secret")]
  [String]$preludeAccountSecret,
  [Parameter(HelpMessage="Probe name")]
  [String]$probeName="raindrop"
)

$PRELUDE_API="https://api.preludesecurity.com"

function LogError {
    param([string]$errStr)
    Write-Host "[!] $errStr" -ForegroundColor Red
}

function LogMessage {
    param([string]$str)
    Write-Host "[+] $str"
}

function Platform {
    if (-not (Test-Path variable:IsWindows) -or $IsWindows) {
        return "windows"
    } else {
        LogError "Platform not supported"
        Exit 1
    }
}

function Architecture {
    # See https://learn.microsoft.com/en-us/dotnet/api/microsoft.powershell.commands.cpuarchitecture?view=powershellsdk-1.1.0
    switch((Get-WMIObject -Class Win32_Processor).Architecture) {
        0 {return "x86_64"}
        9 {return "x86_64"}
        5 {return "arm64"}
        default {
            LogError "Architecture not supported"
            Exit 1
        }
    }

}

function RegisterEndpoint {
    LogMessage "Provisioning Detect Endpoint Token..."
    $data = @{"id"=$env:computername;"tag"="windows"} | ConvertTo-Json
    $response = Invoke-WebRequest -Method POST -Uri $PRELUDE_API/detect/endpoint -Headers @{"account"=$preludeAccountId;"token"=$preludeAccountSecret} -ContentType "application/json" -Body $data
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
        [void](Invoke-WebRequest -Method GET -Uri $PRELUDE_API/download/$probeName -Headers @{"token"=$token;"dos"=$dos} -OutFile $out -PassThru)
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

    $action = New-ScheduledTaskAction -Id $id -Execute $location -WorkingDirectory $wd
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
$dos="$(Platform)-$(Architecture)"
$token=RegisterEndpoint
DownloadProbe $token $dos $probePath
StartTask $token $parentDir $probePath
Write-Host "[=] Detect setup complete"