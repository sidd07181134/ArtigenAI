# Quick ngrok startup script
# Run this AFTER you've authenticated ngrok with your real token

$ngrokPath = "C:\Users\immer\AppData\Local\Temp\ngrok\ngrok.exe"

Write-Host "Starting ngrok tunnel..." -ForegroundColor Green

# Start ngrok
Start-Process -FilePath $ngrokPath -ArgumentList "http","5173" -NoNewWindow

Write-Host "Waiting for tunnel to establish..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Get the public URL
try {
    $tunnels = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    $httpsTunnel = $tunnels.tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
    
    if ($httpsTunnel) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  ✅ TUNNEL ACTIVE!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 YOUR PUBLIC URL:" -ForegroundColor Yellow
        Write-Host $httpsTunnel.public_url -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Share this URL to test your app!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Dashboard: http://localhost:4040" -ForegroundColor Cyan
    } else {
        Write-Host "Tunnel starting... Check http://localhost:4040" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ngrok is starting... Please check http://localhost:4040 for the URL" -ForegroundColor Yellow
}

