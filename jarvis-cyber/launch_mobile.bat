@echo off
REM Launcher do JARVIS para acesso mobile
REM Execute este arquivo para acessar o JARVIS pelo celular

echo ========================================
echo    JARVIS - Acesso Mobile
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python: https://www.python.org/downloads/
    pause
    exit /b
)

echo [1/3] Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Instalando Flask...
    pip install flask flask-socketio
)

echo [2/3] Obtendo IP local...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :break
)
:break
set IP=%IP: =%

echo.
echo ========================================
echo   ACESSO VIA CELULAR
echo ========================================
echo.
echo 1. Conecte seu celular na MESMA rede Wi-Fi
echo 2. Abra o navegador do celular
echo 3. Digite: http://%IP%:5000
echo.
echo ========================================
echo.

echo [3/3] Iniciando servidor JARVIS...
echo.

python web/app.py

pause