[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Log {
    Param([String]$line)

    Write-EventLog -LogName "Application" -Source "Prelude Probe Service" -EventId 0 -Message $line -ErrorAction Ignore
}

function Run {
    Param([String]$Dat = "")

    $Vst = New-Item -Path "$Dir\$(New-Guid).exe" -Force
    $Headers = @{
        'token' = FromEnv "PRELUDE_TOKEN"
        'dos' = $Dos
        'dat' = $Dat
        'version' = "1.0"
    }
    $Response = Invoke-WebRequest -URI $Api -UseBasicParsing -Headers $Headers -MaximumRedirection 1 -OutFile $Vst -PassThru
    $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]

    if ($Response.BaseResponse.ResponseUri -contains "upgrade") {
        Log "[P] Upgrade required" && exit 1
    } elseif (-not $Test) {
        return
    } elseif ($CA -ne $Response.BaseResponse.ResponseUri.Authority) {
        return
    }

    Log "[P] Running $Test [$Vst]"
    $Code = Execute $Vst   
    Run -Dat "${Test}:$Code"
}

function Execute { 
    Param([String]$File)

    try {
        $R = (Start-Process -FilePath $File -Wait -NoNewWindow -PassThru).ExitCode
        $Code = if (Test-Path $File) {$R} Else {127}
        return $Code
    } catch [System.UnauthorizedAccessException] {
        return 126
    } catch [System.InvalidOperationException] {
        return 127
    } catch {
        return 1
    }
}

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$Dir = ".vst"
$Sleep = FromEnv "PRELUDE_SLEEP" 14440
$CA = "prelude-account-prod-us-west-1.s3.amazonaws.com"

$Api = "https://api.preludesecurity.com"
$Dos = "windows-$Env:PROCESSOR_ARCHITECTURE"

while ($true) {
    try {
        Run
        Remove-Item $Dir -Force -Recurse
    } catch { Log $_ }
    Start-Sleep -Seconds $Sleep
}
