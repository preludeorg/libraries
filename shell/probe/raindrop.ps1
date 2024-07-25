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
        Log "Exception: UnauthorizedAccessException - $($_.Exception.Message)"
        return 126
    } catch [System.InvalidOperationException] {
        Log "Exception: InvalidOperationException - $($_.Exception.Message)"
        return 127
    } catch {
        Log "Exception: GenericException - $($_.Exception.Message)"
        return 1
    } finally {
        $logMessageArray = @()
        $stdoutLines = Get-Content -Path $stdoutTempFile | Where-Object { $_ -ne "" }
        if ($stdoutLines) { $logMessageArray += [string]::Join("`n", $stdoutLines) }
        $stderrLines = Get-Content -Path $stderrTempFile | Where-Object { $_ -ne "" }
        if ($stderrLines) { $logMessageArray += [string]::Join("`n", $stderrLines) }
        if ($timeoutVar) { $logMessageArray += $timeoutVar }
        if ($logMessageArray) {
            $logMessageString = [string]::Join("`n", $logMessageArray)
            Log $logMessageString
        }
    }
}

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

function Log { param ([string]$message, [bool]$hostonly = $true)
    if ($host) { Write-Host $message }
    else { Write-Output $message }
    if ($logFileCount -gt 0) { Add-Content -Path $LogFile -Value $message }
}

function RotateLogs {
    $logFiles = Get-ChildItem -Path $logDir -Filter "$baseLogFileName-*.log" | Sort-Object LastWriteTime -Descending

    if ($logFiles.Count -gt $logFileCount) {
        Log "Rotating Logs"
        $logFiles[$logFileCount..($logFiles.Count - 1)] | ForEach-Object { Remove-Item $_.FullName }
        $global:LogFile = Get-LogFileName
        Log "Logs Rotated"
        if ($logEveryoneRead) { icacls $logDir /grant "Everyone:R" /t /c | Out-Null }
    }
    $global:LogFile = Get-LogFileName
}

function Get-LogFileName {
    return Join-Path $logDir "$baseLogFileName-$(Get-Date -Format 'yyyyMMdd').log"
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-east-2.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) ".vst")
$dat = ""
$version = "2.5"
$logDir = FromEnv "PRELUDE_LOGDIR" (Join-Path (Split-Path -Parent $dir) "logs")
$baseLogFileName = "LogFile"
$logFileCount = [int](FromEnv "PRELUDE_LOGCOUNT" 7)
$LogFile = Get-LogFileName
$logEveryoneRead = (FromEnv "PRELUDE_LOGREADEVERYONE" "false") -imatch "^(1|yes|true)$"

if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory | Out-Null
}
if ($logEveryoneRead) { icacls $logDir /grant "Everyone:R" /t /c | Out-Null }

Log "Prelude probe: version ${version}" $false

while ($true) {
    try {
        RotateLogs
        $task = Invoke-WebRequest -Uri "https://api.preludesecurity.com" -Headers @{
            "token" = $env:PRELUDE_TOKEN
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "version" = $version
        } -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue

        $uuid = $task.content -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task.content -replace '^[^/]*//([^/]*)/.*', '$1'

        if ($uuid -and $auth -eq $ca) {
            Log "Downloading $uuid"
            Invoke-WebRequest -Uri $task.content -OutFile (New-Item -path "$dir\$uuid.exe" -Force ) -UseBasicParsing
            Log "Invoking $uuid"
            $code = Execute "$dir\$uuid.exe"
            $dat = "${uuid}:${code}"
            Log "Done Invoking $dat"
        } elseif ($task.content -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Log $_.Exception $false
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = ""
        if (-Not ($task.content -as [int])) {
            Log "Invalid sleep time: $task" $false
            $task = 1800
        }
        Start-Sleep -Seconds "$task"
    }
}
