[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Execute {
    param([String]$File)

    try {
        $process = Start-Process -FilePath $File -NoNewWindow -PassThru
        $handle = $process.Handle
        $process.WaitForExit()
        $exitCode = $process.ExitCode

        if (Test-Path $File) {
            return $exitCode
        } else {
            return 127
        }
    } catch [System.UnauthorizedAccessException] {
        return 126
    } catch [System.InvalidOperationException] {
        return 127
    } catch {
        return 1
    }
}

function FromEnv {
    param([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-east-2.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" $ca
$dat = ""

while ($true) {
    try {
        $task = Invoke-WebRequest -Uri "https://api.preludesecurity.com" -Headers @{
            "token" = $env:PRELUDE_TOKEN
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "version" = "2"
        } -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue

        $uuid = $task.content -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task.content -replace '^[^/]*//([^/]*)/.*', '$1'

        if ($uuid -and $auth -eq $ca) {
            Invoke-WebRequest -Uri $task.content -OutFile (New-Item -path "$dir\$uuid.exe" -Force ) -UseBasicParsing
            $code = Execute "$dir\$uuid.exe"
            $dat = "${uuid}:${code}"
        } elseif ($task -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = ""
        Start-Sleep -Seconds 3600
    }
}
