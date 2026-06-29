# ============================================
# localtunnel 临时公网映射
# 让手机/朋友临时访问本地开发中的网站
# ============================================
# 用法: powershell -ExecutionPolicy Bypass -File tunnel.ps1
# 前提: 已通过 start.ps1 或在另一个终端中启动了应用

$port = if ($args[0]) { $args[0] } else { 8000 }

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  localtunnel 公网映射" -ForegroundColor Cyan
Write-Host "  映射端口: $port" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  启动后会出现一个 URL（如 https://xxx.loca.lt）" -ForegroundColor Yellow
Write-Host "  第一次访问该 URL 需要点击「Click to Continue」" -ForegroundColor Yellow
Write-Host ""
Write-Host "  按 Ctrl+C 停止隧道" -ForegroundColor DarkGray
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

npx localtunnel --port $port

pause
