#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Configuration
Configurações para interface PyQt
"""

import os

# OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'sk-proj-YOUR_API_KEY_HERE')

# Voice Settings
VOICE_RATE = 150
VOICE_VOLUME = 1.0
LISTEN_TIMEOUT = 5
LANGUAGE = 'pt-BR'

# UI Settings
THEME_COLOR = '#4fe0ff'      # Azul neon principal
ACCENT_COLOR = '#00ffd1'     # Ciano
BACKGROUND_COLOR = '#0b0f14' # Preto/azul escuro
TEXT_COLOR = '#cfefff'       # Branco azulado
PANEL_COLOR = '#071017'      # Painel lateral

# Network Settings
NETWORK_SCAN_RANGE = "192.168.1.0/24"
AUTO_SCAN_INTERVAL = 30  # segundos

# System
DEBUG = True
LOG_LEVEL = 'INFO'