# Add your SSH credentials and the remote command here
$sshServer = "10.100.1.3"
$sshUsername = "pocuser"
$sshKeyFile = "C:\Users\pocuser\Downloads\hammer" # Make sure your private key file is in OpenSSH format
$sshCommands = @("./Impairment/0ms/0.5%_Loss.sh", "./Impairment/0ms/1%_Loss.sh", "./Impairment/0ms/1.5%_Loss.sh", "./Impairment/0ms/3%_Loss.sh", "./Impairment/0ms/5%_Loss.sh", "./Impairment/5ms/0%_Loss_5ms_Latency.sh", "./Impairment/5ms/0.5%_Loss_5ms_Latency.sh", "./Impairment/5ms/1%_Loss_5ms_Latency.sh", "./Impairment/5ms/1.5%_Loss_5ms_Latency.sh", "./Impairment/5ms/3%_Loss_5ms_Latency.sh", "./Impairment/5ms/5%_Loss_5ms_Latency.sh", "./Impairment/10ms/0%_Loss_10ms_Latency.sh", "./Impairment/10ms/0.5%_Loss_10ms_Latency.sh", "./Impairment/10ms/1%_Loss_10ms_Latency.sh", "./Impairment/10ms/1.5%_Loss_10ms_Latency.sh", "./Impairment/10ms/3%_Loss_10ms_Latency.sh", "./Impairment/10ms/5%_Loss_10ms_Latency.sh", "./Impairment/15ms/0%_Loss_15ms_Latency.sh", "./Impairment/15ms/0.5%_Loss_15ms_Latency.sh", "./Impairment/15ms/1%_Loss_15ms_Latency.sh", "./Impairment/15ms/1.5%_Loss_15ms_Latency.sh", "./Impairment/15ms/3%_Loss_15ms_Latency.sh", "./Impairment/15ms/5%_Loss_15ms_Latency.sh", "./Impairment/25ms/0%_Loss_25ms_Latency.sh", "./Impairment/25ms/0.5%_Loss_25ms_Latency.sh", "./Impairment/25ms/1%_Loss_25ms_Latency.sh", "./Impairment/25ms/1.5%_Loss_25ms_Latency.sh", "./Impairment/25ms/3%_Loss_25ms_Latency.sh", "./Impairment/25ms/5%_Loss_25ms_Latency.sh", "./Impairment/50ms/0%_Loss_50ms_Latency.sh", "./Impairment/50ms/0.5%_Loss_50ms_Latency.sh", "./Impairment/50ms/1%_Loss_50ms_Latency.sh", "./Impairment/50ms/1.5%_Loss_50ms_Latency.sh", "./Impairment/50ms/3%_Loss_50ms_Latency.sh", "./Impairment/50ms/5%_Loss_50ms_Latency.sh", "./Impairment/75ms/0%_Loss_75ms_Latency.sh", "./Impairment/75ms/0.5%_Loss_75ms_Latency.sh", "./Impairment/75ms/1%_Loss_75ms_Latency.sh", "./Impairment/75ms/1.5%_Loss_75ms_Latency.sh", "./Impairment/75ms/3%_Loss_75ms_Latency.sh", "./Impairment/75ms/5%_Loss_75ms_Latency.sh", "./Impairment/100ms/0%_Loss_100ms_Latency.sh", "./Impairment/100ms/0.5%_Loss_100ms_Latency.sh", "./Impairment/100ms/1%_Loss_100ms_Latency.sh", "./Impairment/100ms/1.5%_Loss_100ms_Latency.sh", "./Impairment/100ms/3%_Loss_100ms_Latency.sh", "./Impairment/100ms/5%_Loss_100ms_Latency.sh")
$RemoveImpairment = "./Impairment/Remove_Impairments.sh"

# File Variables
$file       = "1GB.zip"  # 10MB.zip, 100MB.zip, or 1GB.zip
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
$logFile  = "C:\Users\pocuser\Desktop\log.txt"

# Checking and Logging into OneDrive
$m365Status = m365 status
if ($m365Status -eq "Logged Out") {
    m365 login
}

# Remove Previous Impairments
Write-Host "Removing Any Previously Applied Impairments"
ssh -i $sshKeyFile $sshUsername@$sshServer $RemoveImpairment | Out-Null


# Print out header
Write-host ""
Write-host -ForegroundColor gray "Iteration`tTime`t`tSpeed"
Write-host -ForegroundColor gray "---------`t---------`t------------"

# Download file function
function Download-File() {
    $elapsed = (Measure-Command {m365 spo file get --webUrl $webUrl --url ($url + $file) --asFile --path $desktop}).TotalSeconds
    Set-Variable -Name "speed" -Value (8*(Get-Item $desktop).length/1MB/$elapsed)
    [void]$global:timeArray.Add($elapsed)
    [void]$global:speedArray.Add($speed)
    $output = "$count`t`t" + ([Math]::Round($elapsed, 3)) + "`ts`t" + ([Math]::Round($speed, 2)) + "`tMbps"
    Write-Host $output
    $output | Out-File -Append $logFile
}

for ($j = 0; $j -lt 7; $j++) {
    # Initialize the arrays for each set of 10 downloads
    $global:timeArray  = [System.Collections.ArrayList]::new()
    $global:speedArray = [System.Collections.ArrayList]::new()

    # Download files 5 times
    for ($i = 0; $i -lt 5; $i++) {
        Download-File
        rm $desktop
        $count++
    }

    # Print out Averages
    $timeAvg  = [Math]::Round(($global:timeArray | Measure-Object -Average | select -ExpandProperty Average), 2)
    $speedAvg = [Math]::Round(($global:speedArray | Measure-Object -Average | select -ExpandProperty Average), 2)
    $outputAvg = "Current Average`t`t$timeAvg`ts`t$speedAvg`tMbps"
    Write-Host $outputAvg
    $outputAvg | Out-File -Append $logFile

    # Interactive selection of remote SSH command
    Write-Host "Please choose the script you want to run:"
    for ($i = 0; $i -lt $sshCommands.Count; $i++) {
        Write-Host "$($i+1). $($sshCommands[$i])"
    }
    $selection = Read-Host -Prompt 'Input the number of the script you want to run'
    $selectedCommand = $sshCommands[$selection-1]

    # Execute remote SSH command and ignore output
    ssh -i $sshKeyFile $sshUsername@$sshServer $selectedCommand | Out-Null
}