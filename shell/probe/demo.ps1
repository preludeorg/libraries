[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, HelpMessage="Prelude Token")]
    [String]$preludeToken
)

$PRELUDE_API="https://api.preludesecurity.com"
$TEST_ID="b74ad239-2ddd-4b1e-b608-8397a43c7c54"

if ($Env:PROCESSOR_ARCHITECTURE -eq 'AMD64') {
    $arch = 'x86_64'
} else {
    $arch = 'arm64'
}
$dos = "windows-" + $arch

$TempFile = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "exe") } -PassThru

$Headers = @{
    'token' = $preludeToken
    'dos' = $dos
    'id' = $TEST_ID
}

function CheckRelevance {
    Write-Host "`r`nThis test is designed to be relevant for any workstation or server"
    Write-Host -ForegroundColor Green "`r`n[✓] Result: The test is relevant for your machine"
}

function DownloadTest {
    try {
        Invoke-WebRequest -URI $PRELUDE_API -Headers $Headers -MaximumRedirection 1 -OutFile $TempFile -PassThru | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Host -ForegroundColor Red "`r`n[!] Failed to download test. Http response code: $StatusCode"
        Exit 1
    }
    Write-Host -ForegroundColor Green "`r`n[✓] Wrote to temporary file: $TempFile"
}

function ExecuteTest {
    & $TempFile
    Write-Host -ForegroundColor Green "`r`n[✓] Test is complete"
    return $LASTEXITCODE
}

function ExecuteCleanup {
    & $TempFile clean
    Write-Host -ForegroundColor Green "`r`n[✓] Clean up is complete"
    return $LASTEXITCODE
}

function PostResults {
    param([string]$testresult)
    $Headers.dat = $TEST_ID + ":" + $testresult
    try {
        Invoke-WebRequest -URI $PRELUDE_API -Headers $Headers -MaximumRedirection 1 | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Host -ForegroundColor Red "`r`n[!] Failed to submit results. Http response code: $StatusCode"
        return
    }
    Write-Host -ForegroundColor Green "`r`n[✓] Test result submitted"
}

function InstallProbe {
    Write-Host "`r`n[+] Downloading installation script"
    $temp = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "ps1") } -PassThru

    try {
        Invoke-WebRequest -URI $PRELUDE_API/download/install -Headers $Headers -MaximumRedirection 1 -OutFile $temp -PassThru | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Host -ForegroundColor Red "`r`n[!] Failed to download installation script. Http response code: $StatusCode"
        Exit 1
    }

    $account_id = Read-Host -Prompt "Enter your Prelude Account ID"
    $account_token = Read-Host -Prompt "Enter your Prelude Account token"
    & $temp $account_id $account_token
    Remove-Item $TempFile -Force
}

Write-Host "
###########################################################################################################

Welcome to Prelude!

Rule: Malicious files should quarantine when written to disk
Test: Will your computer quarantine a malicious Office document?

Malicious files are used to gain entry and conduct cyberattacks against corporate systems through seemingly
innocuous email attachments or direct downloads. For example - a malicious macro was used by the BlueNoroff
group in a ransomware attack (Dec. 2022) [link]

[+] CVE mappings: ABC, BCD, CDE, and XXX others [link]
[+] ATT&CK mappings: T1204.002

###########################################################################################################
"
Read-Host -Prompt "Press ENTER to continue"

Write-Host "Starting test at: $(Get-Date -UFormat %T)

-----------------------------------------------------------------------------------------------------------
[0] Conducting relevance test"
Start-Sleep -Seconds 3
CheckRelevance

Write-Host "-----------------------------------------------------------------------------------------------------------
[1] Downloading test"
DownloadTest

Write-Host "-----------------------------------------------------------------------------------------------------------
[2] Executing test
"
Start-Sleep -Seconds 3
$testresult = ExecuteTest

Write-Host "-----------------------------------------------------------------------------------------------------------
[3] Running cleanup
"
Start-Sleep -Seconds 3
$cleanresult = ExecuteCleanup
Remove-Item $TempFile -Force

Write-Host "-----------------------------------------------------------------------------------------------------------
[4] Saving results"
Start-Sleep -Seconds 3
$Status = ($testresult, $cleanresult | Measure-Object -Maximum).Maximum
PostResults $Status

Write-Host "-----------------------------------------------------------------------------------------------------------"

$msg = "[Optional] Would you like to install this test so it runs daily? (y/n)"
do {
    $response = Read-Host -Prompt $msg
    if ($response -eq 'y') {
        InstallProbe
    }
} until ($response -eq 'n' -or $response -eq 'y')

Write-Host "
###########################################################################################################

###########################################################################################################
"

if ($Status -eq 100 ) {
    Write-Host "[✓] Good job! Your computer detected and responded to a malicious Office document dropped on the disk" -ForegroundColor Green
} else {
    Write-Host "[!] This test was able to verify the existence of this vulnerability on your machine, as well as drop a malicious
Office document on the disk. If you have security controls in place that you suspect should have protected your
host, you can use the artifacts above to try to understand why your defenses failed in your logs." -ForegroundColor Red
}

Write-Host "
[*] To view your results for this test and others, run additional tests, or learn about conducting continuous security
tests across your infrastructure, return to platform.preludesecurity.com.

###########################################################################################################
"