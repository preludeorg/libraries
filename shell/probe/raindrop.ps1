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

    $TestExit = Execute $TempFile
    Start-Process -FilePath $TempFile -ArgumentList "clean" -Wait -NoNewWindow -PassThru

    Remove-Item $TempFile -Force
    Run -Dat $($Test + ":" + $TestExit)
}

function Execute { 
    Param([String]$File)
    try {
        return (Start-Process -FilePath $File -Wait -NoNewWindow -PassThru).ExitCode
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
$Token = FromEnv "PRELUDE_TOKEN" ""
$CA = FromEnv "PRELUDE_CA" ""
$Dos = "windows-" + $Env:PROCESSOR_ARCHITECTURE

while ($true) {
    Run
    Start-Sleep -Seconds 14400
}
