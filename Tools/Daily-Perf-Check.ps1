# File Variables
$file       = "100MB.zip"  # 10MB.zip, 100MB.zip, or 1GB.zip
$results    = [System.Collections.Generic.List[PSObject]]::new()
$count      = 1

# Services to check
$servicesToCheck = @("BrinkAgent", "BrinkSupport")

# Determine if this VM is running BrinkAgent or not
$packageName = "BrinkAgent"
$cbInstalled = (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -Match $packageName }) -ne $null

# Check services
$servicesStatus = $true
foreach ($service in $servicesToCheck) {
    $serviceStatus = Get-Service -Name $service -ErrorAction SilentlyContinue
    if (-not $serviceStatus) {
        Write-Host "Service $service not found"
        $servicesStatus = $false
        break
    }
    elseif ($serviceStatus.Status -ne "Running") {
        Write-Host "Service $service is not running"
        $servicesStatus = $false
        break
    }
}

# Exit if any service is not running or not found
if (-not $servicesStatus) {
    Write-Host "Exiting script due to service issues"
    $currentDate = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile  = "C:\Users\pocuser\Documents\Daily Reports\LAST-RUN-FAILED$currentDate.txt"
    "Service check failed at $currentDate" | Out-File -Path $logFile
    exit
}

if ($cbInstalled) {
    $cbStatus = "wCB"
} else {
    $cbStatus = "noCB"
}

# Create a log file with current date and time in the name
$currentDate = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile  = "C:\Users\pocuser\Documents\Daily Reports\CB-Perf-Log$currentDate.csv"

# OneDrive Variables
$webUrl   = "https://cloudbrinkio-my.sharepoint.com/personal/john_cloudbrink_io"
$url      = "/personal/john_cloudbrink_io/Documents/Demo/" + $cbStatus + "/"
$desktop  = "C:\Users\pocuser\Desktop\" + $file

# Checking and Logging into OneDrive
$m365Status = m365 status
if ($m365Status -eq "Logged Out") {
    m365 login
}

# Download file function
function Download-File() {
    $elapsed = (Measure-Command {m365 spo file get --webUrl $webUrl --url ($url + $file) --asFile --path $desktop}).TotalSeconds
    $bandwidth = (8*(Get-Item $desktop).length/1MB/$elapsed)

    $output = New-Object PSObject -Property @{
        Iteration = $count
        Time = [Math]::Round($elapsed, 3)
        Bandwidth = [Math]::Round($bandwidth, 2)
    }
    $results.Add($output)

    Write-Host ("{0}`t`t{1}`ts`t{2}`tMbps" -f $output.Iteration, $output.Time, $output.Bandwidth)
}

# Download files
for ($i = 0; $i -lt 100; $i++)
{
    Download-File
    rm $desktop
    $count++
}

# Print out Averages
$timeAvg  = [Math]::Round(($results.Time | Measure-Object -Average | select -ExpandProperty Average), 2)
$bandwidthAvg = [Math]::Round(($results.Bandwidth | Measure-Object -Average | select -ExpandProperty Average), 2)

Write-Host "Average`t`t$timeAvg`ts`t$bandwidthAvg`tMbps"

$results | Export-Csv -Path $logFile -NoTypeInformation