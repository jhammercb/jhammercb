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


Write-host -ForegroundColor gray "Press <ctrl+c> to complete file downloads"
Write-host -ForegroundColor gray "Ensuring we're logged into OneDrive"
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
    Write-host -ForegroundColor gray ("$count`t`t" + ([Math]::Round($elapsed, 3)) + "`ts`t" + ([Math]::Round($speed, 2)) + "`tMbps")
}


# Download files while allowing ctrl-c to break out of loop
[console]::TreatControlCAsInput = $true
while ($true)
{
    Download-File
    rm $desktop
    $count++

    if ([console]::KeyAvailable)
    {
        $key = [system.console]::readkey($true)
        if (($key.modifiers -band [consolemodifiers]"control") -and ($key.key -eq "C"))
        {
            Add-Type -AssemblyName System.Windows.Forms
            if ([System.Windows.Forms.MessageBox]::Show("Are you sure you want to calculate averages and exit?", "Exit Script?", [System.Windows.Forms.MessageBoxButtons]::YesNo) -eq "Yes")
            {
                break
            }
        }
    }
}


# Print out Averages
Write-Output ""
$timeAvg  = [Math]::Round(($timeArray | Measure-Object -Average | select -ExpandProperty Average), 2)
$speedAvg = [Math]::Round(($speedArray | Measure-Object -Average | select -ExpandProperty Average), 2)
Write-host -ForegroundColor gray "Average`t`t" -NoNewline
Write-host "$timeAvg`ts`t$speedAvg`tMbps"


# Open OBS-Studio App
#Start-Process -WorkingDirectory "C:\Program Files\obs-studio\bin\64bit" -FilePath "obs64.exe" -ArgumentList "--startvirtualcam --minimize-to-tray"


# Upload file
# m365 spo file add --webUrl $webUrl --folder $url --path $desktop


# Leave window open
Write-Host ""
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
$input = Read-Host