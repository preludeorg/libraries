[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Execute($File, $StdoutPath, $StderrPath) {
    try {
        $stdoutTempFile = New-Item -path $StdoutPath -Force
        $stderrTempFile = New-Item -path $StderrPath -Force
        $proc = Start-Process -FilePath $File -NoNewWindow -PassThru -RedirectStandardOutput $stdoutTempFile -RedirectStandardError $stderrTempFile

        $proc | Wait-Process -Timeout 45 -ErrorAction SilentlyContinue -ErrorVariable timeoutVar

        if ($timeoutVar) {
            $proc | kill
            Add-Content -Path $stderrTempFile -Value "Timed out: ${timeoutVar}"
            return 102
        }
        $code = if (Test-Path $File) {$proc.ExitCode} Else {127}
        return $code
    } catch [System.UnauthorizedAccessException] {
        Add-Content -Path $stderrTempFile -Value "UnauthorizedAccessException: ${PsItem}"
        return 126
    } catch [System.InvalidOperationException] {
        Add-Content -Path $stderrTempFile -Value "InvalidOperationException: ${PsItem}"
        return 127
    } catch {
        Add-Content -Path $stderrTempFile -Value "Failed to execute: ${PsItem}"
        return 1
    }
}

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-east-2.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" ".vst"
$dat = ""
$version = "2.5"
$logs = $null
$collectLogs = $false

Write-Output "Prelude probe: version ${version}"

while ($true) {
    try {
        $body = [PSCustomObject]@{}
        if ($collectLogs -and $logs) {
            $logStr = [string]::Join("`n", $logs)
            $logStr = $logStr.substring(0, [System.Math]::Min(250000, $logStr.Length))
            $encodedLogs = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($logStr))
            $body = [PSCustomObject]@{"logs"=$encodedLogs}
        }
        $response = Invoke-WebRequest -Uri "https://api.preludesecurity.com" -Headers @{
            "token" = $env:PRELUDE_TOKEN
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "version" = $version
        } -Method "POST" -Body ($body | ConvertTo-Json) -ContentType "application/json" -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue

        $task = ($response.content -split '\n')[0]
        $uuid = $task -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task -replace '^[^/]*//([^/]*)/.*', '$1'
        $collectLogs = $false
        if ( $response.content -match 'collect_logs = (\d)') {
            $collectLogs = $matches[1] -eq "1"
        }

        if ($uuid -and $auth -eq $ca) {
            Invoke-WebRequest -Uri $task -OutFile (New-Item -path "$dir\$uuid.exe" -Force ) -UseBasicParsing
            $stdoutTempFile = "$dir\stdout.log"
            $stderrTempFile = "$dir\stderr.log"
            $code = Execute -File "$dir\$uuid.exe" -StdoutPath $stdoutTempFile -StderrPath $stderrTempFile
            $dat = "${uuid}:${code}"
            $logs = Get-Content $stdoutTempFile, $stderrTempFile
            if ($logs) {
                Write-Host ([string]::Join("; ", $logs))
            }
        } elseif ($task -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = ""
        if (-Not ($task -as [int])) {
            Write-Output "Invalid sleep time: $task"
            $task = 1800
        }
        Start-Sleep -Seconds "$task"
    }
}
