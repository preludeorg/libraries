[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function FromEnv { param ([string]$envVar, [string]$default)
    $envVal = [Environment]::GetEnvironmentVariable($envVar, "Machine")
    if ($envVal) { return $envVal } else { return $default }
}

$ca = FromEnv "PRELUDE_CA" "prelude-account-us2-us-east-1.s3.amazonaws.com"
$dat = ""
$uuid = "b74ad239-2ddd-4b1e-b608-8397a43c7c54"

while ($true) {
    try {
        $task = Invoke-WebRequest -Uri "https://api.us2.preludesecurity.com" -Headers @{
            "token" = FromEnv "PRELUDE_TOKEN"
            "dos" = "windows-$Env:PROCESSOR_ARCHITECTURE"
            "dat" = $dat
            "id" = $uuid
            "version" = "2"
        } -UseBasicParsing
        
        $uuid = $task -replace ".*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}).*", '$1'
        $auth = $task -replace '^[^/]*//([^/]*)/.*', '$1'

        if ($uuid -and $auth -eq $ca) {
            $taskContent = Invoke-WebRequest -Uri $task -UseBasicParsing
            $taskContent.Content | Out-File -FilePath "$ca\$uuid" -Force
            Set-ItemProperty -Path "$ca\$uuid" -Name IsReadOnly -Value $false
            & "$ca\$uuid"; $code = $LASTEXITCODE
            $dat = "${uuid}:$([System.IO.File]::Exists("$ca\$uuid") -and ($code -eq 0) -or ($null -eq $code) -or $code -eq 127)"
            $uuid = $null
        } elseif ($task -eq "stop") {
            exit
        } else {
            throw "Test cycle done"
        }
    } catch {
        Write-Output $_.Exception
        Remove-Item $ca -Force -Recurse -ErrorAction SilentlyContinue
        $dat = $null
        Start-Sleep -Seconds 3600
    }
}