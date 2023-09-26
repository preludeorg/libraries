[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Prelude Token")]
    [String]$preludeToken
)

$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$PRELUDE_API = if ($env:PRELUDE_API) { $env:PRELUDE_API } else { "https://api.preludesecurity.com" };
$PRELUDE_DIR = ".vst";
$DOS = "windows-x86_64"
$PROTECTED = @(0,9,15,100,104,105,106,107,126,127,137)

$symbols = [PSCustomObject] @{
    CHECKMARK = ([char]8730)
}

$Tests = [ordered]@{
    "5ec67dd1-f6a3-4a5e-9d33-62bb64a339f0" = "LockBit Ransomware"
}
$Results = [ordered]@{}

function CheckRelevance {
    Write-Host -NoNewLine "`r`n[ ] Conducting relevance test`r"
    Start-Sleep -Seconds 1
    Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Conducted relevance test: valid server or workstation detected"
}

function DownloadTest {
    Param([string]$TestId, [string]$Temp)
    Write-Host -NoNewLine "`r`n[ ] Downloading test`r"
    $Headers = @{
        "token" = $preludeToken
        "dos" = $dos
        "id" = $TestId
        "version" = "1.2"
    }

    try {
        Invoke-WebRequest -URI $PRELUDE_API -UseBasicParsing -Headers $Headers -MaximumRedirection 1 -OutFile $Temp -PassThru | Out-Null
    } catch {
        Write-Host -ForegroundColor Red "[!] Failed to download test"
        Exit 1
    }
    Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Downloaded test to temporary file: $Temp"
}

function ExecuteTest {
    Param([string]$Temp, [string]$Name)
    Write-Host -NoNewLine "`r`n[ ] Starting test`r"
    Start-Sleep -Seconds 1
    try {
        $p = Start-Process -FilePath $Temp -Wait -NoNewWindow -PassThru
        if ($p.ExitCode -in $PROTECTED ) {
            Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Executed test: control test passed"
        } else {
            Write-Host -ForegroundColor Red "[!] Executed test: control test failed"
        }
        return $p.ExitCode
    } catch [System.InvalidOperationException] {
        Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Executed test: control test passed"
        return 127
    } catch {
        Write-Host -ForegroundColor Red "[!] Executed test: an unexpected error occurred:`r`n"
        Write-Host -ForegroundColor Red  $_
        return 1
    }
}

function ExecuteCleanup {
    Write-Host -NoNewLine "`r`n[ ] Running cleanup`r"
    Start-Sleep -Seconds 1
    Remove-Item "$PRELUDE_DIR\*" -Force -Recurse -ErrorAction Ignore
    if (-Not (Test-Path -Path "$PRELUDE_DIR\*")) {
        Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Clean up is complete"
    } else {
        Write-Host -ForegroundColor Red "[!] Clean up failed"
    }
}

function PostResults {
    param([string]$Id, [string]$Result)
    $Headers = @{
        "token" = $preludeToken
        "dos" = $dos
        "dat" = $Id + ":" + $Result
        "version" = "1.1"
    }
    Invoke-WebRequest -URI $PRELUDE_API -UseBasicParsing -Headers $Headers -MaximumRedirection 1 | Out-Null
}

function RunDemo {
    Param([string]$Id, [string]$Name)
    $Temp = New-Item -Path "$PRELUDE_DIR\$(New-Guid).exe" -Force

    Write-Host "`r`nTest: $Name"
    Write-Host "`r`nMore details at: https://www.preludesecurity.com/advisories/aa23-075a"
    Start-Sleep -Seconds 1
    Write-Host "`r`nStarting test at: $(Get-Date -UFormat %T)"
    CheckRelevance
    DownloadTest $Id $Temp
    $TestResult = ExecuteTest $Temp $Name
    ExecuteCleanup
    PostResults $Id $TestResult

    if ($TestResult -in $PROTECTED ) {
        $Results[$Name] = "PROTECTED"
    } elseif ($TestResult -eq 101) {
        $Results[$Name] = "UNPROTECTED"
    } else {
        $Results[$Name] = "ERROR"
    }

    Write-Host "`r`n###########################################################################################################"
    Start-Sleep -Seconds 2
}

foreach ($i in $Tests.Keys) {
    RunDemo $i $Tests[$i]
}

Remove-Item $PRELUDE_DIR -Force -Recurse -ErrorAction Ignore

Write-Host "[*] Go to https://platform.preludesecurity.com to register for an account`r`n"
