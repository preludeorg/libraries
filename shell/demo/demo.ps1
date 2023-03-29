[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Prelude Token")]
    [String]$preludeToken
)

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$PRELUDE_API = if ($env:PRELUDE_API) { $env:PRELUDE_API } else { "https://api.preludesecurity.com" };
$PRELUDE_DIR = if ($env:PRELUDE_DIR) { $env:PRELUDE_DIR } else { ".vst" };
$DOS = "windows-x86_64"

$symbols = [PSCustomObject] @{
    CHECKMARK = ([char]8730)
}

$Tests = [ordered]@{
    "39de298a-911d-4a3b-aed4-1e8281010a9a" = "Health check"
    "3ebbda49-738c-4799-a8fb-206630cf609e" = "Will a long running VST be stopped properly?"
    "2e705bac-a889-4283-9a8e-a12358fa1d09" = "Will your computer quarantine Royal Ransomware?"
    "b74ad239-2ddd-4b1e-b608-8397a43c7c54" = "Will your computer quarantine a malicious Office document?"
    "ca9b22be-93d5-4902-95f4-4bc43a817b73" = "Will your computer quarantine Colour-Blind malware?"
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
        if ($p.ExitCode -in 100,9,17,18,105,127 ) {
            if (($Name -eq 'Health Check' -or $Name -eq 'Will a long running VST be stopped properly?') -and $p.ExitCode -ne 100) {
                Write-Host -ForegroundColor Yellow "[!] Health check should not be quarantined or blocked"
            } else {
                Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Executed test: control test passed"
            }
        } else {
            Write-Host -ForegroundColor Red "[!] Executed test: control test failed"
        }
        return $p.ExitCode
    } catch [System.InvalidOperationException] {
        if (($Name -eq 'Health Check' -or $Name -eq 'Will a long running VST be stopped properly?') -and $p.ExitCode -ne 100) {
            Write-Host -ForegroundColor Yellow "[!] Health check should not be quarantined or blocked"
        } else {
            Write-Host -ForegroundColor Green "[$($symbols.CHECKMARK)] Executed test: control test passed"
        }
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
    }
    Invoke-WebRequest -URI $PRELUDE_API -UseBasicParsing -Headers $Headers -MaximumRedirection 1 | Out-Null
}

function RunDemo {
    Param([string]$Id, [string]$Name)
    $Temp = New-Item -Path "$PRELUDE_DIR\$(New-Guid).exe" -Force

    Write-Host "`r`nTest: $Name"
    Write-Host "`r`nMore details at: https://github.com/preludeorg/test/tree/master/tests/$Id"
    Start-Sleep -Seconds 1
    Write-Host "`r`nStarting test at: $(Get-Date -UFormat %T)"
    CheckRelevance
    DownloadTest $Id $Temp
    $TestResult = ExecuteTest $Temp $Name
    ExecuteCleanup
    PostResults $Id $TestResult

    if ($TestResult -in 100,9,17,18,105,127 ) {
        $Results[$Name] = "PROTECTED"
    } elseif ($TestResult -eq 101) {
        $Results[$Name] = "UNPROTECTED"
    } else {
        $Results[$Name] = "ERROR"
    }

    Write-Host "`r`n###########################################################################################################"
    if ($Id -eq '3ebbda49-738c-4799-a8fb-206630cf609e') {
        Write-Host "`r`n`r`nCompleted Health Check tests. Beginning quarantine tests.`r`n"
        Write-Host "`r`n###########################################################################################################"
    }
    Start-Sleep -Seconds 2
}

Write-Host "`r`n###########################################################################################################"
Write-Host "`r`n`r`nRunning safety checks to ensure quarantine tests will run as expected.`r`n"
Write-Host "`r`n###########################################################################################################"

foreach ($i in $Tests.Keys) {
    RunDemo $i $Tests[$i]
}

Remove-Item $PRELUDE_DIR -Force -Recurse -ErrorAction Ignore

Write-Host "###########################################################################################################"
Write-Host "`r`nSummary of test results:"
$Results.GetEnumerator()  | Format-Table @{
    Label="Test";
    Expression={
        switch ($_.Value) {
            "PROTECTED" { $color = "32"; break }
            "UNPROTECTED" { $color = "31"; break }
            "ERROR" { $color = "33"; break }
            default { $color = "0" }
        }
        $e = [char]27
       "$e[${color}m$($_.Key)${e}[0m"
    }
}, @{
    Label="Result";
    Expression={
        switch ($_.Value) {
            "PROTECTED" { $color = "32"; break }
            "UNPROTECTED" { $color = "31"; break }
            "ERROR" { $color = "33"; break }
            default { $color = "0" }
        }
        $e = [char]27
       "$e[${color}m$($_.Value)${e}[0m"
    }
}

Write-Host "Go to https://platform.preludesecurity.com to register for an account`r`n"
