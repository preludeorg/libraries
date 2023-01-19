function Run {
    Param([String]$Dat = "")

    $TempFile = [System.IO.Path]::GetTempFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "exe") } -PassThru

    $Headers = @{
        'token' = $Token
        'dos' = $Dos
        'dat' = $Dat
    }
    try {
        $Response = Invoke-WebRequest -URI $Address -UseBasicParsing -Headers $Headers -MaximumRedirection 1 -OutFile $TempFile -PassThru
    } catch {
        $StatusCode = $_.Exception.Response.StatusCode.value__
        Write-Output "ERROR: Failed to reach Prelude Service. " + $StatusCode
        return
    }
    if ($CA -and $CA -ne $Response.BaseResponse.ResponseUri.Authority) {
        return
    }
    $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]
    if (-not $Test) {
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

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Address = if ($Env:PRELUDE_API) { $Env:PRELUDE_API } else { "https://api.preludesecurity.com/" }
$Token = if ($Env:PRELUDE_TOKEN) { $Env:PRELUDE_TOKEN } else { "" }
$CA = if ($Env:PRELUDE_CA) { $Env:PRELUDE_CA } else { "" }
$Dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE

while ($true) {
    Run
    Start-Sleep -Seconds 43200
}