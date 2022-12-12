                    function Run {
    Param([String]$Dat = "")

    $TempFile = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "exe") } -PassThru

    $Headers = @{
        'token' = $Token
        'dos' = $Dos
        'dat' = $Dat
    }
    try {
        $Response = Invoke-WebRequest -URI $Address -Headers $Headers -MaximumRedirection 1 -OutFile $TempFile -PassThru
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Output "ERROR: Failed to reach Prelude Service. " + $StatusCode
        return
    }
    $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]
    if ($Test -eq "") {
        Write-Output "INFO: Done running tests"
        return
    }

    & $TempFile
    $TestExit = $LASTEXITCODE
    & $TempFile clean
    $CleanExit = $LASTEXITCODE

    $Status = $Test + ":" + ($TestExit, $CleanExit | Measure-Object -Maximum).Maximum

    Remove-Item $TempFile -Force
    Run -Dat $Status
}

$Address = if ($Env:PRELUDE_API) { $Env:PRELUDE_API } else { "https://detect.prelude.org/" }
$Token = if ($Env:PRELUDE_TOKEN) { $Env:PRELUDE_TOKEN } else { "" }

if ($Env:PROCESSOR_ARCHITECTURE -eq 'AMD64') {
    $Arch = 'x86_64'
} else {
    $Arch = 'arm64'
}
$Dos = "windows-" + $Arch

while ($true) {
    Run
    Start-Sleep -Seconds 43200
}