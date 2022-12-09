[CmdletBinding()]
param(
  [Parameter(Mandatory=$true, HelpMessage="Probe name")]
  [String]$probeName,
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Id")]
  [String]$preludeAccountId,
  [Parameter(Mandatory=$true, HelpMessage="Prelude Account Secret")]
  [String]$preludeAccountSecret
)

$PRELUDE_API="https://detect.prelude.org"
$PROBE_NAME=$probeName
$PRELUDE_ACCOUNT_ID=$preludeAccountId
$PRELUDE_ACCOUNT_SECRET=$preludeAccountSecret

function LogError {
    param([string]$errStr)
    Write-Host "[!] $errStr" -ForegroundColor Red
}

function LogMessage {
    param([string]$str)
    Write-Host "[+] $str"
}

function Platform {
    if ($IsLinux) {
        return "linux"
    } elseif ($IsMacOS) {
        return "darwin"
    } elseif (-not (Test-Path variable:IsWindows) -or $IsWindows) {
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
    $response = Invoke-WebRequest -Method POST -Uri $PRELUDE_API/account/endpoint -Headers @{"account"="$PRELUDE_ACCOUNT_ID";"token"="$PRELUDE_ACCOUNT_SECRET"} -ContentType "application/json" -Body $data
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
        Invoke-WebRequest -Method GET -Uri $PRELUDE_API/download/$PROBE_NAME -Headers @{"token"="$token";"dos"="$dos"} -OutFile $out -PassThru
    } catch [System.Net.WebException] { 
        LogError "Detect failed to download! $($_.ErrorDetails)"
        Exit 1
    } 
}

function StartService {
    param([string]$token, [string]$location)
    $name = "Prelude Detect"
    $svc = Get-WmiObject -Class Win32_Service -Filter "Name='$name'"
    if($svc.Length -ne 0) {
        $svc.delete()
    }
    [System.Environment]::SetEnvironmentVariable("PRELUDE_TOKEN", $token, "User")
    $svc = New-Service -Name $name -DisplayName $name -BinaryPathName $location -StartupType "Automatic"
    $svc.start()
}

LogMessage "Detect setup started"
$probePath=(Join-Path ([System.Environment]::ExpandEnvironmentVariables("%LOCALAPPDATA%")) "prelude" | Join-Path -ChildPath $PROBE_NAME) + ".exe"
if(Test-Path -path $probePath -PathType Leaf) {
    Remove-Item $probeDownloadPath
}
LogMessage "Determining OS"
$dos="$(Platform)-$(Architecture)"
$token=RegisterEndpoint
DownloadProbe $token $dos $probePath
StartService $token $probePath
Write-Host "[=] Detect setup complete"