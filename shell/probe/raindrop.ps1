[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

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

$Dir = FromEnv "PRELUDE_DIR" ".vst"
$CA = "prelude-account-us1-us-west-1.s3.amazonaws.com"

$Api = "https://api.preludesecurity.com"
$Dos = "windows-$Env:PROCESSOR_ARCHITECTURE"
$Dat = ""

while ($true) {
    try {
        $Vst = New-Item -Path "$Dir\0" -Force
        $Headers = @{
            'token' = FromEnv "PRELUDE_TOKEN"
            'dos' = $Dos
            'dat' = $Dat
            'version' = "1.1"
        }
        $Response = Invoke-WebRequest -URI $Api -UseBasicParsing -Headers $Headers -MaximumRedirection 1 -OutFile $Vst -PassThru
        $Test = $Response.BaseResponse.ResponseUri.AbsolutePath.Split("/")[-1].Split("_")[0]
    
        if ($Test) {
            if ($Test -icontains "upgrade") {
                Write-Output "[P] Upgrade required"
                exit 1
            } elseif ($CA -eq $Response.BaseResponse.ResponseUri.Authority) {
                Rename-Item -Path "$Dir\0" -NewName "$Dir\$Test.exe"
                $Code = Execute $Vst
                $Dat = "${Test}:$Code"
            }
        } else {
            throw "Tests completed"
        }
    } catch {
        Write-Output $_.Exception
        $Dat = ""
        Remove-Item $Dir -Force -Recurse -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 14440
    }
}
