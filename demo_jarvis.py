#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração Básica do JARVIS
Mostra funcionalidades principais sem dependências de áudio
"""

import sys
import os
import time

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.config_manager import ConfigManager
from core.logger import setup_logging, JarvisLogger
from core.events import EventManager, Events
from ai.brain import AIBrain

def demo_jarvis():
    """Demonstração básica do JARVIS"""
    print("🤖 JARVIS - Demonstração Básica")
    print("=" * 40)
    
    # Configurar logging
    setup_logging()
    logger = JarvisLogger('demo')
    
    # Carregar configuração
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    if not config:
        print("❌ Erro ao carregar configuração")
        return
    
    # Inicializar motor de IA
    logger.system("Inicializando JARVIS...")
    brain = AIBrain(config)
    
    # Simular alguns comandos
    test_commands = [
        "olá",
        "como você está?",
        "que horas são?",
        "acenda as luzes da sala",
        "obrigado",
        "tchau"
    ]
    
    print("\n🎯 Testando comandos de voz:")
    print("-" * 40)
    
    for command in test_commands:
        print(f"\n👤 Usuário: {command}")
        
        # Simular comando de voz
        response = brain._try_predefined_response(command)
        
        if response:
            if callable(response):
                response = response()
            print(f"🤖 JARVIS: {response}")
        else:
            print("🤖 JARVIS: Comando não reconhecido em modo demonstração.")
        
        time.sleep(1)  # Pausa para simular processamento
    
    print("\n" + "=" * 40)
    print("✅ Demonstração concluída!")
    print("\nPara uso completo:")
    print("1. Configure OpenAI API key em config/config.json")
    print("2. Execute: python main.py")
    print("3. Acesse interface web: http://localhost:5000")

if __name__ == "__main__":
    try:
        demo_jarvis()
    except KeyboardInterrupt:
        print("\n\n👋 Demonstração interrompida pelo usuário")