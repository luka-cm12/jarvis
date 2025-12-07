#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Assistente Pessoal Inteligente
Versão simplificada para resolver problemas de threading
"""

import sys
import os
import signal
import asyncio
from pathlib import Path

# Adicionar diretório src ao path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Imports principais
from core.config_manager import ConfigManager
from core.logger import setup_logging, JarvisLogger
from web.app import JarvisWebInterface

def signal_handler(sig, frame):
    """Handler para sinais do sistema"""
    logger = JarvisLogger(__name__)
    logger.system("Sinal recebido: desligando JARVIS...")
    sys.exit(0)

def main():
    """Função principal simplificada"""
    
    # Banner ASCII
    print("""
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
    """)
    
    print("🔵 Inicializando sistemas...")
    
    # Configurar logging
    setup_logging()
    logger = JarvisLogger(__name__)
    
    # Configurar signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Carregar configurações
        config = ConfigManager()
        logger.system("Configurações carregadas")
        
        logger.system("🌐 Iniciando interface web do JARVIS...")
        
        # Criar interface web e executar diretamente
        web_interface = JarvisWebInterface(config)
        web_interface.run(threaded=False)  # Executar sem threading
        
    except KeyboardInterrupt:
        logger.system("Interrupção recebida - finalizando...")
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        return 1
    
    logger.system("🔴 JARVIS finalizado")
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)