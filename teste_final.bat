@echo off
echo.
echo =====================================================
echo          TESTE FINAL DO JARVIS
echo =====================================================
echo.

:: Ativar ambiente virtual
call venv\Scripts\activate.bat

echo 🧪 Executando testes com ambiente virtual ativado...
echo.

:: Teste básico de funcionamento
echo 🔍 Teste 1: Demonstração básica
python demo_jarvis.py

echo.
echo 🔍 Teste 2: Testes completos
python test_jarvis.py

echo.
echo 🎯 Testes concluídos!
echo.
echo Para usar o JARVIS:
echo 1. Execute: iniciar_jarvis.bat
echo 2. Ou: python main.py (com venv ativado)
echo 3. Interface web: python src\web\app.py
echo.
pause