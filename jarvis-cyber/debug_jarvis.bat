@echo off
chcp 65001 > nul
title JARVIS - Depuração
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════
echo             🔍 JARVIS - SISTEMA DE DEPURAÇÃO
echo ═══════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

python debug_jarvis.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar depuração
    echo.
    pause
    exit /b 1
)

echo.
pause
