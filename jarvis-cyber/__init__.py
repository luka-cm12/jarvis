#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security System
Sistema completo de cibersegurança ética
"""

__version__ = "1.0.0"
__author__ = "JARVIS Security Team"
__email__ = "security@jarvis.ai"
__description__ = "Sistema de cibersegurança ética inspirado no JARVIS"

# Importações principais
try:
    from .server import app as server
    from .tools import scanner, firewall, hardening
    from .models import local_model
    from .agent import agent
except ImportError:
    # Para execução standalone
    pass

# Configurações padrão
DEFAULT_CONFIG = {
    "server": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": False
    },
    "security": {
        "jwt_secret": "jarvis-cyber-security-system",
        "token_expiry": 3600,
        "max_scan_range": 1024
    },
    "features": {
        "ai_enabled": True,
        "voice_enabled": False,
        "lab_mode": True
    }
}

# Mensagem de inicialização
STARTUP_MESSAGE = """
🤖 JARVIS Cyber Security System v{version}
🛡️  Sistema de segurança ética para profissionais
⚖️  Use apenas com autorização e responsabilidade
""".format(version=__version__)

def print_startup():
    """Exibir mensagem de inicialização"""
    print(STARTUP_MESSAGE)