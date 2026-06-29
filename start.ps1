# ============================================
# 辩论AI辅助写作系统 — Windows 一键启动脚本
# ============================================
# 用法: 右键点击「以 PowerShell 运行」
# 或: powershell -ExecutionPolicy Bypass -File start.ps1

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  辩论AI辅助写作系统 — 启动脚本" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# 检查 Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "[错误] 未找到 Python，请先安装 Python 3.11+" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[✓] Python: $($python.Source)" -ForegroundColor Green

# 检查虚拟环境
$venvPath = Join-Path $PSScriptRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[*] 正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv $venvPath
    if (-not $?) {
        Write-Host "[错误] 虚拟环境创建失败" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "[✓] 虚拟环境已创建" -ForegroundColor Green
}

# 激活虚拟环境
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
. $activate

# 安装依赖
Write-Host "[*] 正在安装依赖..." -ForegroundColor Yellow
pip install -r (Join-Path $PSScriptRoot "requirements.txt") -q
if (-not $?) {
    Write-Host "[错误] 依赖安装失败" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "[✓] 依赖已安装" -ForegroundColor Green

# 加载 .env 中的环境变量
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)=(.*)") {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
    Write-Host "[✓] .env 配置文件已加载" -ForegroundColor Green
}

# 启动应用
Write-Host "[*] 正在启动应用..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  本地访问: http://localhost:8000" -ForegroundColor White
Write-Host "  远程访问: http://<你的IP>:8000" -ForegroundColor White
Write-Host ""
Write-Host "  按 Ctrl+C 停止服务" -ForegroundColor DarkGray
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

python (Join-Path $PSScriptRoot "run.py")

pause
