# PowerShell script to download a file multiple times, measure download time and speed, and calculate averages.
# Reach out to john@cloudbrink.com if any issues

# Define Variables
$fileName       = "100MB.zip"  # Name of the file to download
$downloadUrl    = "https://cloudbrinkio-my.sharepoint.com/personal/john_cloudbrink_io/_layouts/15/download.aspx?share=EXMSDrRYFulJkeHK-UvKBnYBxfHWYqVxXBM-16e6rzy3VA"
$iterations     = 10           # Number of times to download the file

$results        = [System.Collections.Generic.List[PSObject]]::new()

# Determine Download and Log Paths

# Get the Downloads folder path
$shell = New-Object -ComObject Shell.Application
$downloadFolder = $shell.Namespace('shell:Downloads').Self.Path

$destinationPath = Join-Path $downloadFolder $fileName

# Get the Documents folder path
$logFolder = [Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments)
$logFolder = Join-Path $logFolder 'Logs'

# Ensure that the log folder exists
if (!(Test-Path $logFolder)) {
    New-Item -ItemType Directory -Path $logFolder | Out-Null
}

# Create a log file with current date and time in the name
$currentDate = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $logFolder "CB-Perf-Log_$currentDate.csv"

# Print out header
Write-Host ""
Write-Host -ForegroundColor Gray "Iteration`tTime (s)`tSpeed (Mbps)"
Write-Host -ForegroundColor Gray "---------`t---------`t------------"

# Function to download the file and measure time and speed
function Download-File {
    param(
        [string]$downloadUrl,
        [string]$destinationPath,
        [int]$iteration
    )

    # Create WebClient instance
    $webClient = New-Object System.Net.WebClient
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        # Download the file
        $webClient.DownloadFile($downloadUrl, $destinationPath)
        $stopwatch.Stop()

        if (Test-Path $destinationPath) {
            $fileSizeBytes = (Get-Item $destinationPath).Length
            $elapsed = $stopwatch.Elapsed.TotalSeconds
            # Calculate speed in Mbps
            $speed = (8 * $fileSizeBytes / 1MB) / $elapsed
        } else {
            $elapsed = 0
            $speed = 0
            Write-Host "Download failed on iteration $iteration."
        }
    } catch {
        $stopwatch.Stop()
        $elapsed = 0
        $speed = 0
        # Use string formatting to avoid the colon issue
        Write-Host ("Error downloading file on iteration {0}: {1}" -f $iteration, $_.Exception.Message)
    } finally {
        $webClient.Dispose()
    }

    # Store the results
    $output = [PSCustomObject]@{
        Iteration = $iteration
        Time      = [Math]::Round($elapsed, 3)
        Speed     = [Math]::Round($speed, 2)
    }
    $results.Add($output)

    # Output the results for this iteration
    Write-Host ("{0}`t`t{1}`t`t{2}`tMbps" -f $output.Iteration, $output.Time, $output.Speed)
}

# Download files multiple times
for ($i = 1; $i -le $iterations; $i++) {
    Download-File -downloadUrl $downloadUrl -destinationPath $destinationPath -iteration $i
    # Remove the downloaded file
    if (Test-Path $destinationPath) {
        Remove-Item $destinationPath -Force
    }
}

# Calculate and display averages
$timeAvg  = [Math]::Round(($results.Time | Measure-Object -Average | Select -ExpandProperty Average), 2)
$speedAvg = [Math]::Round(($results.Speed | Measure-Object -Average | Select -ExpandProperty Average), 2)
$outputAvg = [PSCustomObject]@{
    Iteration = "Average"
    Time      = $timeAvg
    Speed     = $speedAvg
}
$results.Add($outputAvg)

Write-Host ("{0}`t`t{1}`t`t{2}`tMbps" -f $outputAvg.Iteration, $outputAvg.Time, $outputAvg.Speed)

# Export results to CSV file
$results | Export-Csv -Path $logFile -NoTypeInformation

# Keep the console window open
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
[void][System.Console]::ReadKey($true)
