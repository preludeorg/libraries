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

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Process")
    if($envVal) return $envVal
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "User")
    return if ($envVal) { $envVal } else { $default }
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Address = FromEnv "PRELUDE_API" "https://api.preludesecurity.com"
$Token = FromEnv "PRELUDE_TOKEN" ""
$CA = FromEnv "PRELUDE_CA" ""
$Dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE

while ($true) {
    Run
    Start-Sleep -Seconds 43200
}