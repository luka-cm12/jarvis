#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Production Server
Servidor de produção do JARVIS com configurações otimizadas
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def create_logs_directory():
    """Cria diretório de logs se não existir"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print("📁 Diretório de logs criado")

def start_with_waitress():
    """Inicia servidor com Waitress (recomendado para Windows)"""
    print("🚀 Iniciando JARVIS com servidor de produção Waitress...")
    
    try:
        from waitress import serve
        from web_server import app
        
        print("\n" + "="*60)
        print("🤖 JARVIS PRODUCTION SERVER v2.0")
        print("="*60)
        print("🌐 Servidor: Waitress (Production Grade)")
        print("📡 URL: http://localhost:5000")
        print("📱 Mobile: http://localhost:5000/mobile")
        print("⚠️  Use Ctrl+C para parar o servidor")
        print("="*60 + "\n")
        
        # Configurar SSL se certificados estiverem disponíveis
        ssl_cert = Path("ssl/certificate.crt")
        ssl_key = Path("ssl/private.key")
        
        if ssl_cert.exists() and ssl_key.exists():
            print("🔒 Certificados SSL detectados - Habilitando HTTPS")
            serve(app, 
                  host='0.0.0.0', 
                  port=5000,
                  threads=8,
                  cleanup_interval=30,
                  channel_timeout=120)
        else:
            serve(app, 
                  host='0.0.0.0', 
                  port=5000,
                  threads=8,
                  cleanup_interval=30,
                  channel_timeout=120)
                  
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def start_with_gunicorn():
    """Inicia servidor com Gunicorn (recomendado para Linux)"""
    print("🚀 Iniciando JARVIS com Gunicorn...")
    
    # Instalar eventlet para suporte ao SocketIO
    try:
        import eventlet
    except ImportError:
        print("📦 Instalando eventlet para suporte ao SocketIO...")
        subprocess.run([sys.executable, "-m", "pip", "install", "eventlet"], check=True)
    
    cmd = [
        "gunicorn",
        "--config", "gunicorn.conf.py",
        "wsgi:application"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar Gunicorn: {e}")

def main():
    """Função principal"""
    create_logs_directory()
    
    print("🤖 JARVIS Production Server Launcher")
    print("Escolha o servidor de produção:")
    print("1. Waitress (Recomendado para Windows)")
    print("2. Gunicorn (Recomendado para Linux)")
    print("3. Auto-detectar")
    
    choice = input("\nEscolha (1-3) [3]: ").strip() or "3"
    
    if choice == "1":
        start_with_waitress()
    elif choice == "2":
        start_with_gunicorn()
    else:
        # Auto-detectar sistema operacional
        if os.name == 'nt':  # Windows
            start_with_waitress()
        else:  # Linux/Mac
            start_with_gunicorn()

if __name__ == "__main__":
    main()