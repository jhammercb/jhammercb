# File Variables
$file       = "100MB.zip"  # 10MB.zip, 100MB.zip, or 1GB.zip
$timeArray  = [System.Collections.ArrayList]::new()
$speedArray = [System.Collections.ArrayList]::new()
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
$desktop  = "C:\Users\pocuser\Desktop\" + $file
$logFile  = "C:\Users\pocuser\Desktop\log.txt" # New log file path

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
    Set-Variable -Name "speed" -Value (8*(Get-Item $desktop).length/1MB/$elapsed)
    [void]$timeArray.Add($elapsed)
    [void]$speedArray.Add($speed)
    $output = "$count`t`t" + ([Math]::Round($elapsed, 3)) + "`ts`t" + ([Math]::Round($speed, 2)) + "`tMbps"
    Write-Host $output
    $output | Out-File -Append $logFile
}

# Download files
for ($i = 0; $i -lt 100; $i++)
{
    Download-File
    rm $desktop
    $count++
}

# Print out Averages
$timeAvg  = [Math]::Round(($timeArray | Measure-Object -Average | select -ExpandProperty Average), 2)
$speedAvg = [Math]::Round(($speedArray | Measure-Object -Average | select -ExpandProperty Average), 2)
$outputAvg = "Average`t`t$timeAvg`ts`t$speedAvg`tMbps"
Write-Host $outputAvg
$outputAvg | Out-File -Append $logFile

# Leave window open
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
$input = Read-Host