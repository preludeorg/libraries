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

$ca = FromEnv "PRELUDE_CA" "prelude-account-us1-us-west-1.s3.amazonaws.com"
$dir = FromEnv "PRELUDE_DIR" ".vst"
$dat = ""
$uuid = "b74ad239-2ddd-4b1e-b608-8397a43c7c54"

while ($true) {
    try {
        $task = Invoke-WebRequest -Uri "https://api.us2.preludesecurity.com" -Headers @{
            "token" = $env:PRELUDE_TOKEN
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "id" = $uuid
            "version" = "2"
        } -UseBasicParsing
        
        $uuid = $task -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task -replace '^[^/]*//([^/]*)/.*', '$1'

        if ($uuid -and $auth -eq $ca) {
            $taskContent = Invoke-WebRequest -Uri $task -UseBasicParsing
            $taskContent.Content | Out-File -FilePath "$dir\$uuid.exe" -Force
            $code = Execute "$dir\$uuid.exe"
            $dat = "$uuid:$code"
            $uuid = $null
        } elseif ($task -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $dir -Force -Recurse -ErrorAction SilentlyContinue
        $dat = $null
        Start-Sleep -Seconds 3600
    }
}