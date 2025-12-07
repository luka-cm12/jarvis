#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Production Launcher
Launcher de produção sem avisos de desenvolvimento
"""

import sys
import os
from pathlib import Path

# Suprimir avisos de desenvolvimento
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

def main():
    """Inicializar servidor de produção"""
    try:
        print("🚀 Inicializando JARVIS Production Server...")
        
        # Tentar usar Waitress primeiro (melhor para Windows)
        try:
            from waitress import serve
            from web_server import app
            
            print("\n" + "="*70)
            print("🤖 JARVIS ADVANCED ASSISTANT - PRODUCTION MODE")
            print("="*70)
            print("🔧 Servidor: Waitress (Production Grade)")
            print("🌐 URL Principal: http://localhost:5000")
            print("📱 Interface Móvel: http://localhost:5000/mobile")
            print("🔒 Modo: Produção (Sem avisos de desenvolvimento)")
            print("⚠️  Pressione Ctrl+C para parar")
            print("="*70)
            
            # Configurações de produção otimizadas
            serve(
                app,
                host='localhost',
                port=5000,
                threads=6,              # Múltiplas threads
                cleanup_interval=30,    # Limpeza periódica
                channel_timeout=300,    # Timeout de 5 minutos
                max_request_body_size=10485760,  # 10MB max
                expose_tracebacks=False  # Não expor tracebacks
            )
            
        except ImportError:
            print("⚠️  Waitress não encontrado, usando Flask diretamente...")
            print("💡 Para melhor performance, instale: pip install waitress")
            
            from web_server import socketio, app
            
            socketio.run(
                app,
                host='localhost',
                port=5000,
                debug=False,
                use_reloader=False
            )
            
    except KeyboardInterrupt:
        print("\n🛑 JARVIS finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())