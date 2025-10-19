@echo off
echo.
echo =====================================================
echo          JARVIS - Assistente Pessoal Inteligente
echo =====================================================
echo.

:: Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado!
    echo Por favor instale Python 3.9+ em https://python.org
    pause
    exit /b 1
)

:: Verificar se ambiente virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

:: Verificar se dependências estão instaladas
python -c "import speech_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando dependências pela primeira vez...
    echo Isso pode demorar alguns minutos...
    pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar dependências!
        echo Verifique sua conexão com a internet e tente novamente.
        pause
        exit /b 1
    )
)

:: Verificar se config existe
if not exist "config\config.json" (
    if exist "config\config.example.json" (
        echo Copiando arquivo de configuração...
        copy "config\config.example.json" "config\config.json" >nul
        echo.
        echo ATENÇÃO: Configure suas API keys em config\config.json
        echo Pressione qualquer tecla para continuar ou Ctrl+C para sair
        pause >nul
    ) else (
        echo ERRO: Arquivo config.example.json não encontrado!
        pause
        exit /b 1
    )
)

:: Criar diretórios necessários
if not exist "logs" mkdir logs
if not exist "data" mkdir data

echo.
echo Iniciando JARVIS...
echo Para parar, pressione Ctrl+C
echo.

:: Executar JARVIS
python main.py

echo.
echo JARVIS finalizado.
pause