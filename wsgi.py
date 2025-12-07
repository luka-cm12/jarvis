#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Production WSGI Entry Point
Ponto de entrada WSGI para produção
"""

import sys
import os
from pathlib import Path

# Adicionar diretório do projeto ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Importar aplicação
from web_server import app, socketio

# Aplicação WSGI
application = app

if __name__ == "__main__":
    # Para execução direta
    socketio.run(app, host='0.0.0.0', port=5000)