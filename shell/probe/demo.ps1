[CmdletBinding()]
param(
  [Parameter(Mandatory=$true, HelpMessage="Prelude Token")]
  [String]$preludeToken
)

$PRELUDE_API="https://api.preludesecurity.com/"
$TEST_ID="b74ad239-2ddd-4b1e-b608-8397a43c7c54"

if ($Env:PROCESSOR_ARCHITECTURE -eq 'AMD64') {
    $Arch = 'x86_64'
} else {
    $Arch = 'arm64'
}
$dos = "windows-" + $Arch

$TempFile = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "exe") } -PassThru

$Headers = @{
    'token' = $preludeToken
    'dos' = $dos
    'id' = $TEST_ID
}

function CheckRelevance {
    Write-Host "This test is relevant for any laptop or server."
}

function DownloadTest {
    try {
        Invoke-WebRequest -URI $PRELUDE_API -Headers $Headers -MaximumRedirection 1 -OutFile $TempFile -PassThru | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Output "ERROR: Failed to reach Prelude Service. " + $StatusCode
        return
    }
    Write-Host "[✓] Wrote to temporary file: " + $TempFile
}

function ExecuteTest {
    & $TempFile
    Write-Host "`r`n[✓] Test is complete"
    return $LASTEXITCODE
}

function ExecuteCleanup {
    & $TempFile clean
    Write-Host "`r`n[✓] Clean up is complete"
    return $LASTEXITCODE
}

function PostResults {
    param([string]$testresult)
    $Headers.dat = $testresult
    try {
        Invoke-WebRequest -URI $PRELUDE_API -Headers $Headers -MaximumRedirection 1 | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Output "ERROR: Failed to reach Prelude Service. " + $StatusCode
        return
    }
    Write-Host "[✓] Test result submitted"
}

function InstallProbe {
    Write-Host "[+] Downloading installation script"
    Write-Host $PRELUDE_API/download/install
    $temp = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "ps1") } -PassThru

    try {
        Invoke-WebRequest -URI $PRELUDE_API/download/install -Headers $Headers -MaximumRedirection 1 -OutFile $temp -PassThru | Out-Null
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Output "ERROR: Failed to reach Prelude Service. " + $StatusCode
        return
    }

    $account_id = Read-Host -Prompt "Enter your Prelude Account ID"
    $account_token = Read-Host -Prompt "Enter your Prelude Account token"
    Write-Host $account_id $account_token
    & $temp -a $account_id -s $account_token
    Remove-Item $TempFile -Force
}

Write-Host "
###########################################################################################################

Will your computer quarantine a malicious Office document?

[*] There have been 1,798 CVE numbers tied to malicious Office documents
[*] MITRE ATT&CK classifies a malicious Office macro as technique T1204.002
[*] A malicious macro was used by the BlueNoroff group in a ransomware attack (Dec. 2022)

###########################################################################################################
"
Read-Host -Prompt "Press ENTER to continue"

Write-Host "
Starting test at: $(Get-Date -UFormat %T)

-----------------------------------------------------------------------------------------------------------
[0] Checking relevance
"
Start-Sleep -Seconds 3
CheckRelevance

Write-Host "
-----------------------------------------------------------------------------------------------------------
[1] Downloading test
"
DownloadTest

Write-Host "
-----------------------------------------------------------------------------------------------------------
[2] Executing test
"
Start-Sleep -Seconds 3
$testresult = ExecuteTest

Write-Host "
-----------------------------------------------------------------------------------------------------------
[3] Running cleanup
"
Start-Sleep -Seconds 3
$cleanresult = ExecuteCleanup
Remove-Item $TempFile -Force

Write-Host "
-----------------------------------------------------------------------------------------------------------
[4] Saving results
"
Start-Sleep -Seconds 3
$Status = $TEST_ID + ":" + ($testresult, $cleanresult | Measure-Object -Maximum).Maximum
PostResults $Status

Write-Host "
-----------------------------------------------------------------------------------------------------------
"

$msg = "[Optional] Would you like to install this test so it runs daily? (y/n) "
do {
    $response = Read-Host -Prompt $msg
    if ($response -eq 'y') {
        InstallProbe
    }
} until ($response -eq 'n' -or $response -eq 'y')

Write-Host "



###########################################################################################################
"

#if [ "$test_result" = 100 ];then
#    echo "[✓] Good job! Your computer detected and responded to a malicious Office document dropped on the disk."
#else
#    echo "[!] Your computer was unable to detect a malicious Office document dropped on the disk."
#    echo "[!] Reach out to support@prelude.org for help selecting an appropriate endpoint defense."
#fi


Write-Host "
[*] Learn more about tests you can run: https://docs.prelude.org/docs/the-basics

###########################################################################################################
"