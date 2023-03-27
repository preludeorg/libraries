[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Log {
    Param([String]$line)

    Write-EventLog -LogName "Application" -Source "Prelude Detect" -EventId 0 -Message $line -ErrorAction Ignore
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
$Dat = ""
New-EventLog –LogName Application –Source 'Prelude Detect' -ErrorAction Ignore

while ($true) {
    try {
        $Vst = New-Item -Path "$Dir\$(New-Guid).exe" -Force
        $Headers = @{
            'token' = FromEnv "PRELUDE_TOKEN"
            'dos' = $Dos
            'dat' = $Dat
            'version' = "1.0"
        }
        $Response = Invoke-WebRequest -URI $Api -UseBasicParsing -Headers $Headers -MaximumRedirection 1 -OutFile $Vst -PassThru
        $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]
    
        if ($Test) {
            if ($CA -eq $Response.BaseResponse.ResponseUri.Authority) {
                Log "[P] Running $Test [$Vst]"
                $Code = Execute $Vst   
                $Dat = "${Test}:$Code"
            }
        } elseif ($Response.BaseResponse.ResponseUri -contains "upgrade") {
            Log "[P] Upgrade required"
            exit 1
        } else {
            Remove-Item $Dir -Force -Recurse
            Start-Sleep -Seconds $Sleep
        }
    } catch { 
        Log $_
        Start-Sleep -Seconds $Sleep
    }
}
