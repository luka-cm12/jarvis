#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS PyQt Demo
Demonstração das funcionalidades do JARVIS PyQt
"""

import sys
import time
from pathlib import Path

# Adicionar path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from main_simple import SimpleJarvisUI
except ImportError:
    print("❌ PyQt5 não encontrado. Execute: pip install PyQt5")
    sys.exit(1)

def demo_commands():
    """Lista de comandos para demonstração"""
    return [
        "olá jarvis",
        "que horas são",
        "abrir youtube", 
        "abrir spotify",
        "abrir google",
        "sair"
    ]

def show_demo_info():
    """Mostrar informações da demonstração"""
    commands = demo_commands()
    
    info = """
🤖 JARVIS PyQt - Demonstração

📋 Comandos de Voz Disponíveis:
    
🗣️  Comandos Básicos:
    • "Olá JARVIS" - Saudação
    • "Que horas são" - Horário atual
    • "Sair" - Encerrar sistema
    
🌐 Comandos de Navegação:
    • "Abrir YouTube" - Abre YouTube
    • "Abrir Spotify" - Abre Spotify 
    • "Abrir Google" - Abre Google
    
🎮 Como Usar:
    1. Clique no botão "🎤 OUVIR"
    2. Aguarde o indicador "OUVINDO..."
    3. Fale um dos comandos acima
    4. Aguarde a resposta do JARVIS
    
⚙️  Recursos da Interface:
    • Design estilo Jarvis (azul neon)
    • Log de conversa em tempo real
    • Síntese de voz (TTS)
    • Reconhecimento de voz (STT)
    • Botão de limpeza do log
    
✨ Características:
    • Interface responsiva
    • Processamento em threads separadas
    • Tratamento de erros robusto
    • Configuração via JSON
    • Estilo visual Homem de Ferro
    
🔧 Configuração:
    Edite qt_interface/config/config.json para personalizar:
    • Cores da interface
    • Velocidade da fala
    • Idioma do reconhecimento
    • Outras configurações
"""
    
    return info

def main():
    """Função principal da demo"""
    app = QApplication(sys.argv)
    
    # Mostrar informações
    info_box = QMessageBox()
    info_box.setWindowTitle('JARVIS PyQt - Demo')
    info_box.setText(show_demo_info())
    info_box.setIcon(QMessageBox.Information)
    
    # Customizar botões
    info_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    info_box.button(QMessageBox.Ok).setText('Iniciar JARVIS')
    info_box.button(QMessageBox.Cancel).setText('Cancelar')
    
    result = info_box.exec_()
    
    if result == QMessageBox.Ok:
        # Iniciar JARVIS
        try:
            window = SimpleJarvisUI()
            window.show()
            
            # Log de boas-vindas
            window.add_log("🎯 DEMO MODE ATIVADO", "system")
            window.add_log("💡 Use comandos como: 'olá jarvis', 'que horas são', 'abrir youtube'", "system")
            window.add_log("🎤 Clique no botão OUVIR para começar", "system")
            
            return app.exec_()
            
        except Exception as e:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle('Erro')
            error_box.setText(f'Erro ao inicializar JARVIS:\n\n{str(e)}')
            error_box.exec_()
            return 1
    else:
        return 0

if __name__ == '__main__':
    sys.exit(main())