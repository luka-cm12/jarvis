#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Assistente Pessoal Inteligente
Arquivo principal de inicialização do sistema
"""

import sys
import os
import logging
import asyncio
from pathlib import Path

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from enhanced_jarvis import EnhancedJARVIS as JARVIS
from core.config_manager import ConfigManager
from core.logger import setup_logging

def main():
    """Função principal de inicialização do JARVIS"""
    try:
        # Configurar logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Banner de inicialização
        print_banner()
        
        # Carregar configurações
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        if not config:
            logger.error("Falha ao carregar configurações. Verifique config/config.json")
            return
        
        # Inicializar JARVIS
        logger.info("Inicializando JARVIS...")
        jarvis = JARVIS(config)
        
        # Executar em loop assíncrono
        asyncio.run(jarvis.run())
        
    except KeyboardInterrupt:
        logger.info("JARVIS desligado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

def print_banner():
    """Exibe o banner de inicialização do JARVIS"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║         ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                  ║
    ║         ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                  ║
    ║         ██║███████║██████╔╝██║   ██║██║███████╗                  ║
    ║    ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                  ║
    ║    ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                  ║
    ║     ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                  ║
    ║                                                                   ║
    ║              Assistente Pessoal Inteligente v1.0                 ║
    ║                "Just A Rather Very Intelligent System"           ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("\n🔵 Inicializando sistemas...")

if __name__ == "__main__":
    main()