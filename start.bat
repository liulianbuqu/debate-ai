@echo off
chcp 65001 >nul
title 辩论AI辅助写作系统

echo ========================================
echo    ? 辩论AI辅助写作系统
echo    ========================================
echo.
echo  正在启动服务...
echo  访问地址: http://localhost:8000
echo.
echo  按 Ctrl+C 停止服务
echo.
python run.py
pause
