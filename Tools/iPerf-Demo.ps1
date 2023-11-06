Write-Host "Starting UDP Based iPerf Test"
Write-Host "iperf3 -c 34.168.129.177 -p 7001 -i 1 -u -l 100 -b 300M"

C:\iperf3 -c 34.168.129.177 -p 7001 -i 1 -u -l 100 -b 300M

# Leave window open
Write-Host ""
Write-Host "Press Enter to exit" -ForegroundColor Gray -NoNewline
$input = Read-Host