# File Variables
$file       = "100MB.zip"  # 10MB.zip, 100MB.zip, or 1GB.zip
$results    = [System.Collections.Generic.List[PSObject]]::new()
$count      = 1

# Determine if this VM is running BrinkAgent or not
$packageName = "BrinkAgent"
$cbInstalled = (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where { $_.DisplayName -Match $packageName }) -ne $null
if ($cbInstalled) {
    $cbStatus = "wCB"
} else {
    $cbStatus = "noCB"
}

# OneDrive Variables
$webUrl   = "https://cloudbrinkio-my.sharepoint.com/personal/john_cloudbrink_io"
$url      = "/personal/john_cloudbrink_io/Documents/Demo/" + $cbStatus + "/"
$desktop  = "C:\Users\johnh\Downloads\" + $file

# Create a log file with current date and time in the name
$currentDate = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile  = "C:\Users\johnh\Documents\Logs\CB-Perf-Log$currentDate.csv"

# Checking and Logging into OneDrive
$m365Status = m365 status
if ($m365Status -eq "Logged Out") {
    m365 login
}

# Print out header
Write-host ""
Write-host -ForegroundColor gray "Iteration`tTime`t`tSpeed"
Write-host -ForegroundColor gray "---------`t---------`t------------"

# Download file function
function Download-File() {
    $elapsed = (Measure-Command {m365 spo file get --webUrl $webUrl --url ($url + $file) --asFile --path $desktop}).TotalSeconds
    $speed = (8*(Get-Item $desktop).length/1MB/$elapsed)
    
    $output = New-Object PSObject -Property @{
        Iteration = $count
        Time = [Math]::Round($elapsed, 3)
        Speed = [Math]::Round($speed, 2)
    }
    $results.Add($output)

    Write-Host ("{0}`t`t{1}`ts`t{2}`tMbps" -f $output.Iteration, $output.Time, $output.Speed)
}

# Download files
for ($i = 0; $i -lt 10; $i++)
{
    Download-File
    rm $desktop
    $count++
}

# Print out Averages
$timeAvg  = [Math]::Round(($results.Time | Measure-Object -Average | select -ExpandProperty Average), 2)
$speedAvg = [Math]::Round(($results.Speed | Measure-Object -Average | select -ExpandProperty Average), 2)
$outputAvg = New-Object PSObject -Property @{
    Iteration = "Average"
    Time = $timeAvg
    Speed = $speedAvg
}
$results.Add($outputAvg)

Write-Host ("{0}`t`t{1}`ts`t{2}`tMbps" -f $outputAvg.Iteration, $outputAvg.Time, $outputAvg.Speed)

$results | Export-Csv -Path $logFile -NoTypeInformation

# Leave window open
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
$input = Read-Host