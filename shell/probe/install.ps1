[CmdletBinding()]
param(
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Id")]
  [String]$preludeAccountId,
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Secret")]
  [String]$preludeAccountSecret,
  [Parameter(HelpMessage="Probe name")]
  [String]$probeName="raindrop",
  [Parameter(HelpMessage="Endpoint id")]
  [String]$endpointId=$env:computername
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

function RegisterEndpoint {
    LogMessage "Provisioning Detect Endpoint Token..."
    $data = @{"id"=$endpointId;"tag"="windows"} | ConvertTo-Json
    $RequestParams = @{"Method"="POST";"Uri"=$PRELUDE_API/detect/endpoint;"Headers"=@{"account"=$preludeAccountId;"token"=$preludeAccountSecret};"ContentType"="application/json";"Body"=$data}
    if ($Proxy) {
        $RequestParams.add("Proxy", $Proxy)
        $RequestParams.add("ProxyUseDefaultCredentials", $true)
    }
    $response = Invoke-RestMethod @RequestParams
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
        $RequestParams = @{"Method"="GET";"Uri"=$PRELUDE_API/download/$probeName;"Headers"=@{"token"=$token;"dos"=$dos};"OutFile"=$out;"PassThru"=$true}
        if ($Proxy) {
            $RequestParams.add("Proxy", $Proxy)
            $RequestParams.add("ProxyUseDefaultCredentials", $true)
        }
        [void](Invoke-RestMethod @RequestParams)
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
$dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE
$SystemProxy = [System.Net.WebRequest]::GetSystemWebProxy()
if ($SystemProxy) {
    $SystemProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials;
    if (($SystemProxy.GetProxy($Address)) -notcontains $Address) {
        $Proxy = $SystemProxy.GetProxy($Address)
    }
}
$token=RegisterEndpoint
DownloadProbe $token $dos $probePath
StartTask $token $parentDir $probePath
Write-Host "[=] Detect setup complete"
