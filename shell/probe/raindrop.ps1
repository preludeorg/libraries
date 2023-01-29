function Run {
    Param([String]$Dat = "")

    $FileName = [System.IO.Path]::GetRandomFileName() | Rename-Item -NewName { [System.IO.Path]::ChangeExtension($_, "exe") } -PassThru
    $TempFile = Join-Path $WorkingDirectory $FileName

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
        return $TempFile
    }
    if ($CA -and $CA -ne $Response.BaseResponse.ResponseUri.Authority) {
        return $TempFile
    }
    $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]
    if (-not $Test) {
        Write-Output "INFO: Done running tests"
        return $TempFile
    }

    $TestExit = Execute $TempFile
    Start-Process -FilePath $TempFile -ArgumentList "clean" -Wait -NoNewWindow -PassThru

    Remove-Item $TempFile -Force
    Run -Dat $($Test + ":" + $TestExit)
}

function Execute {
    Param([String]$File)
    try {
        return (Start-Process -FilePath $File -Wait -NoNewWindow -PassThru).ExitCode
    } catch [System.UnauthorizedAccessException] {
        return 126
    } catch [System.InvalidOperationException] {
        return 127
    } catch {
        Write-Host $_
        return 1
    }
}

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "User")
    if ($envVal) { return $envVal } else { return $default }
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$Address = FromEnv "PRELUDE_API" "https://api.preludesecurity.com"
$WorkingDirectory = FromEnv "PRELUDE_DIR" [System.IO.Path]::GetTempPath()
$Token = FromEnv "PRELUDE_TOKEN" ""
$CA = FromEnv "PRELUDE_CA" ""
$Dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE

while ($true) {
    $TempFile = Run
    Remove-Item $TempFile -Force
    Start-Sleep -Seconds 14400
}
