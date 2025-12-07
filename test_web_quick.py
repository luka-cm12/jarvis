#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Rápido da Interface Web
"""

import sys
import os

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_web_quick():
    """Teste rápido da interface web"""
    try:
        from core.config_manager import ConfigManager
        from web.app import JarvisWebInterface
        
        print("🌐 Testando Interface Web...")
        
        # Carregar configuração
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Criar interface web
        web_interface = JarvisWebInterface(config)
        
        print("✅ Interface web criada com sucesso!")
        print("🔗 Para executar: python src/web/app.py")
        print("🌐 URL: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na interface web: {e}")
        return False

if __name__ == "__main__":
    test_web_quick()