#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Interface Web do JARVIS
"""

import sys
import os
import threading
import time

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.config_manager import ConfigManager
from web.app import JarvisWebInterface

def test_web_interface():
    """Testa a interface web"""
    print("🌐 Testando Interface Web do JARVIS")
    print("=" * 40)
    
    # Carregar configuração
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Criar interface web
    web_interface = JarvisWebInterface(config)
    
    print("📡 Iniciando servidor web...")
    print("🔗 Acesse: http://localhost:5000")
    print("⏹️  Pressione Ctrl+C para parar")
    print("-" * 40)
    
    try:
        # Executar servidor
        web_interface.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor web parado pelo usuário")

if __name__ == "__main__":
    test_web_interface()