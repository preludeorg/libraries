[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Execute {
    Param([String]$File)

    try {
        $stdoutTempFile = New-Item -path "$dir\stdout.log" -Force
        $stderrTempFile = New-Item -path "$dir\stderr.log" -Force
        $proc = Start-Process -WorkingDirectory "$dir" -FilePath $File -NoNewWindow -PassThru -RedirectStandardOutput $stdoutTempFile -RedirectStandardError $stderrTempFile

        $proc | Wait-Process -Timeout 45 -ErrorAction SilentlyContinue -ErrorVariable timeoutVar

        if ($timeoutVar) {
            $proc | kill
            return 102
        }

        $code = if (Test-Path $File) {$proc.ExitCode} Else {127}
        return $code
    } catch [System.UnauthorizedAccessException] {
        "System.UnauthorizedAccessException - $File" | Out-File -FilePath $stderrTempFile -Append
        return 126
    } catch [System.InvalidOperationException] {
        "System.InvalidOperationException - $File" | Out-File -FilePath $stderrTempFile -Append
        return 127
    } catch {
        return 1
    } finally {
        $stdout = Get-Content -Path $stdoutTempFile
        $stdout = if ($stdout) { [string]::Join("; ", $stdout) } else { "" }
        $stderr = Get-Content -Path $stderrTempFile
        $stderr = if ($stderr) { [string]::Join("; ", $stderr) } else { "" }

        if ($stdout -or $stderr -or $timeoutVar) {
            Write-Host "${stdout}; ${stderr}; ${timeoutVar}"
        }
    }
}

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-east-2.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" ".vst"
$dat = ""
$version = "2.7"

Write-Output "Prelude probe: version ${version}"

while ($true) {
    try {
        $task = Invoke-WebRequest -Uri "https://api.preludesecurity.com" -Headers @{
            "token" = $env:PRELUDE_TOKEN
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "version" = $version
        } -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue

        $uuid = $task.content -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task.content -replace '^[^/]*//([^/]*)/.*', '$1'

        if ($uuid -and $auth -eq $ca) {
            Invoke-WebRequest -Uri $task.content -OutFile (New-Item -path "$dir\$uuid.exe" -Force ) -UseBasicParsing
            $code = Execute "$dir\$uuid.exe"
            $dat = "${uuid}:${code}"
        } elseif ($task.content -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = ""
        if (-Not ($task.content -as [int])) {
            Write-Output "Invalid sleep time: $task"
            $task = 1800
        }
        Start-Sleep -Seconds "$task"
    }
}
