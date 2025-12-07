@echo off
echo.
echo     ╔═══════════════════════════════════════════════════════════════════╗
echo     ║                     JARVIS PyQt Interface                        ║
echo     ║                   Launcher para Windows                          ║
echo     ╚═══════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.7+ primeiro.
    pause
    exit /b 1
)

echo Verificando dependências...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo ⚠️  PyQt5 não encontrado. Instalando...
    pip install PyQt5
)

python -c "import speech_recognition" 2>nul
if errorlevel 1 (
    echo ⚠️  SpeechRecognition não encontrado. Instalando...
    pip install SpeechRecognition
)

python -c "import pyttsx3" 2>nul
if errorlevel 1 (
    echo ⚠️  pyttsx3 não encontrado. Instalando...
    pip install pyttsx3
)

echo.
echo 🚀 Iniciando JARVIS PyQt Interface...
echo.
python main_simple.py

if errorlevel 1 (
    echo.
    echo ❌ Erro ao executar JARVIS
    pause
)

echo.
echo ✅ JARVIS encerrado normalmente
pause