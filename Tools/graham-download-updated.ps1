 # Define the available file sizes and URLs
$sizes = @(
    @{ Size = "5MB"; URL = "http://212.183.159.230/5MB.zip" },
    @{ Size = "10MB"; URL = "http://212.183.159.230/10MB.zip" },
    @{ Size = "20MB"; URL = "http://212.183.159.230/20MB.zip" },
    @{ Size = "50MB"; URL = "http://212.183.159.230/50MB.zip" },
    @{ Size = "100MB"; URL = "http://212.183.159.230/100MB.zip" },
    @{ Size = "200MB"; URL = "http://212.183.159.230/200MB.zip" },
    @{ Size = "512MB"; URL = "http://212.183.159.230/512MB.zip" },
    @{ Size = "1GB"; URL = "http://212.183.159.230/1GB.zip" }
)

# Display the available options
Write-Host "Select a file size to download:"
for ($i = 0; $i -lt $sizes.Count; $i++) {
    Write-Host "$($i + 1). $($sizes[$i].Size)"
}

# Prompt user for selection
$sizeSelection = Read-Host "Enter the number corresponding to the file size"

# Validate input
while (-not ([int]::TryParse($sizeSelection, [ref]$null)) -or $sizeSelection -lt 1 -or $sizeSelection -gt $sizes.Count) {
    Write-Host "Invalid selection. Please enter a number between 1 and $($sizes.Count)."
    $sizeSelection = Read-Host "Enter the number corresponding to the file size"
}

# Get the selected size and URL
$selectedSize = $sizes[$sizeSelection - 1]
$url = $selectedSize.URL
$fileSize = $selectedSize.Size

# Define the file name
$fileName = "$fileSize.zip"

# Prompt for number of download iterations
$numDLInput = Read-Host "Enter the number of download iterations (default is 10)"
if ([string]::IsNullOrWhiteSpace($numDLInput)) {
    $numDL = 10
} elseif (-not [int]::TryParse($numDLInput, [ref]$null)) {
    Write-Host "Invalid input. Using default value of 10."
    $numDL = 10
} else {
    $numDL = [int]$numDLInput
}

# Initialize the results list
$results = [System.Collections.Generic.List[PSObject]]::new()

# Get the Downloads folder path
$shell = New-Object -ComObject Shell.Application
$downloadFolder = $shell.Namespace('shell:Downloads').Self.Path

$destinationPath = Join-Path $downloadFolder $fileName

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
for ($i = 1; $i -le $numDL; $i++) {
    Download-File -downloadUrl $url -destinationPath $destinationPath -iteration $i
    # Remove the downloaded file
    if (Test-Path $destinationPath) {
        Remove-Item $destinationPath -Force
    }
}

# Calculate and display averages
$timeAvg  = [Math]::Round(($results.Time | Measure-Object -Average | Select -ExpandProperty Average), 3)
$speedAvg = [Math]::Round(($results.Speed | Measure-Object -Average | Select -ExpandProperty Average), 2)
$outputAvg = [PSCustomObject]@{
    Iteration = "Average"
    Time      = $timeAvg
    Speed     = $speedAvg
}
$results.Add($outputAvg)

Write-Host ("{0}`t`t{1}`t`t{2}`tMbps" -f $outputAvg.Iteration, $outputAvg.Time, $outputAvg.Speed)

# Keep the console window open
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
[void][System.Console]::ReadKey($true) 
