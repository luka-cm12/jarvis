#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Interface Web Responsiva
Funciona em Desktop e Mobile
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import os
import sys
import threading
import time
from datetime import datetime

# Adicionar path das ferramentas
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jarvis_secret_key_2025'
socketio = SocketIO(app, cors_allowed_origins="*")

# Status global do sistema
system_status = {
    'online': True,
    'last_update': datetime.now().isoformat(),
    'active_scans': 0,
    'total_scans': 0,
    'security_score': 0
}

@app.route('/')
def index():
    """Página principal do JARVIS"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API de status do sistema"""
    system_status['last_update'] = datetime.now().isoformat()
    return jsonify(system_status)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API para executar scan"""
    try:
        data = request.get_json()
        target = data.get('target', '127.0.0.1')
        
        # Importar ferramenta de scan
        from tools.simple_tools import run_quick_scan
        
        system_status['active_scans'] += 1
        result = run_quick_scan(target)
        system_status['active_scans'] -= 1
        system_status['total_scans'] += 1
        
        # Emitir resultado via WebSocket
        socketio.emit('scan_result', {
            'target': target,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        system_status['active_scans'] = max(0, system_status['active_scans'] - 1)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hardening', methods=['POST'])
def api_hardening():
    """API para avaliação de segurança"""
    try:
        from tools.simple_tools import run_quick_assessment
        
        result = run_quick_assessment()
        system_status['security_score'] = result.get('overall_score', 0)
        
        # Emitir resultado via WebSocket
        socketio.emit('hardening_result', {
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice', methods=['POST'])
def api_voice():
    """API para processamento de comandos de voz"""
    try:
        data = request.get_json()
        command = data.get('command', '').lower()
        
        response = "Comando não reconhecido"
        action = None
        
        if 'scan' in command or 'escanear' in command:
            response = "Iniciando varredura de rede..."
            action = 'scan'
        elif 'segurança' in command or 'hardening' in command:
            response = "Executando avaliação de segurança..."
            action = 'hardening'
        elif 'status' in command:
            response = f"Sistema operacional. Score de segurança: {system_status['security_score']}/100"
            action = 'status'
        elif 'olá' in command or 'oi' in command or 'hello' in command:
            response = "Olá! Sou o JARVIS. Como posso ajudá-lo com a segurança?"
            action = 'greeting'
        
        return jsonify({
            'success': True,
            'response': response,
            'action': action
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@socketio.on('connect')
def handle_connect():
    """Cliente conectado"""
    emit('status_update', system_status)

@socketio.on('request_status')
def handle_status_request():
    """Solicitação de status"""
    system_status['last_update'] = datetime.now().isoformat()
    emit('status_update', system_status)

def update_status_loop():
    """Loop para atualizar status periodicamente"""
    while True:
        time.sleep(30)  # Atualizar a cada 30 segundos
        system_status['last_update'] = datetime.now().isoformat()
        socketio.emit('status_update', system_status)

if __name__ == '__main__':
    print("🚀 Iniciando JARVIS Web Interface...")
    print("📱 Acesse: http://localhost:5000")
    print("💻 Compatível com Desktop e Mobile")
    
    # Iniciar thread de atualização de status
    status_thread = threading.Thread(target=update_status_loop, daemon=True)
    status_thread.start()
    
    # Iniciar servidor
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)