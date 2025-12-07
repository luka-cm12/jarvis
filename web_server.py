#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Advanced Web Interface
Interface web avançada com capacidades de rede e IA
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
import time
import threading
import json
import sys
import os
from pathlib import Path

# Adicionar src ao path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from modules.network_scanner import NetworkScanner, NetworkMonitor
    from ai.advanced_brain import AdvancedAI
    from modules.mobile_manager import MobileDeviceManager
    from modules.pentest_system import NetworkPenetrationTester
    ADVANCED_FEATURES = True
except ImportError as e:
    print(f"⚠️  Funcionalidades avançadas não disponíveis: {e}")
    ADVANCED_FEATURES = False

# Criar aplicação Flask
app = Flask(__name__, template_folder='src/web/templates', static_folder='src/web/static')
app.config['SECRET_KEY'] = 'jarvis_secret_key_2024'

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Tempo de início do sistema
start_time = time.time()

# Status do sistema
system_status = {
    'online': True,
    'last_update': time.time(),
    'version': '2.0 Advanced',
    'modules': ['voice', 'ai', 'automation', 'learning', 'network_scanner'],
    'network_devices': 0,
    'vulnerabilities_found': 0,
    'ai_learning_active': True
}

connected_clients = 0

# Inicializar componentes avançados
if ADVANCED_FEATURES:
    print("🚀 Inicializando componentes avançados...")
    try:
        network_scanner = NetworkScanner()
        network_monitor = NetworkMonitor()
        advanced_ai = AdvancedAI()
        mobile_manager = MobileDeviceManager()
        pentest_system = NetworkPenetrationTester()
        print("✅ Componentes avançados carregados")
    except Exception as e:
        print(f"❌ Erro ao carregar componentes: {e}")
        ADVANCED_FEATURES = False
else:
    network_scanner = None
    network_monitor = None
    advanced_ai = None
    mobile_manager = None
    pentest_system = None

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API de status do sistema"""
    return jsonify(system_status)

@app.route('/api/command', methods=['POST'])
def api_command():
    """API para enviar comandos"""
    data = request.get_json()
    command = data.get('command', '')
    
    if command:
        # Processar comando com IA avançada se disponível
        if ADVANCED_FEATURES and advanced_ai:
            try:
                ai_response = advanced_ai.generate_response(command)
                
                # Emitir resposta da IA
                socketio.emit('ai_response', {
                    'response': ai_response,
                    'timestamp': time.time(),
                    'advanced': True
                })
                
                return jsonify({
                    'success': True, 
                    'message': 'Comando processado pela IA avançada',
                    'ai_response': ai_response
                })
            except Exception as e:
                print(f"Erro na IA avançada: {e}")
        
        # Fallback para resposta simples
        socketio.emit('voice_command', {
            'command': command,
            'timestamp': time.time(),
            'source': 'api'
        })
        
        return jsonify({'success': True, 'message': 'Comando recebido'})
    
    return jsonify({'success': False, 'error': 'Comando inválido'}), 400

@app.route('/api/network/scan', methods=['POST'])
def api_network_scan():
    """API para scan de rede"""
    if not ADVANCED_FEATURES or not network_scanner:
        return jsonify({'success': False, 'error': 'Scanner de rede não disponível'}), 503
    
    try:
        # Executar scan em thread separada
        def run_scan():
            results = network_scanner.full_network_scan()
            system_status['network_devices'] = len(results)
            
            # Contar vulnerabilidades
            total_vulns = sum(len(data.get('vulnerabilities', [])) for data in results.values())
            system_status['vulnerabilities_found'] = total_vulns
            
            # Emitir resultados
            socketio.emit('network_scan_complete', {
                'results': results,
                'summary': {
                    'devices_found': len(results),
                    'vulnerabilities': total_vulns
                },
                'timestamp': time.time()
            })
        
        scan_thread = threading.Thread(target=run_scan, daemon=True)
        scan_thread.start()
        
        return jsonify({'success': True, 'message': 'Scan de rede iniciado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/network/report')
def api_network_report():
    """API para relatório de rede"""
    if not ADVANCED_FEATURES or not network_scanner:
        return jsonify({'success': False, 'error': 'Scanner de rede não disponível'}), 503
    
    try:
        report = network_scanner.get_network_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai/stats')
def api_ai_stats():
    """API para estatísticas da IA"""
    if not ADVANCED_FEATURES or not ai_brain:
        return jsonify({'success': False, 'error': 'Cérebro AI não disponível'}), 503
    
    try:
        stats = {
            'memory_entries': len(getattr(ai_brain, 'memory', [])),
            'learning_patterns': len(getattr(ai_brain, 'learning_patterns', [])),
            'status': 'active',
            'uptime': int(time.time() - start_time) if 'start_time' in globals() else 0
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/mobile')
def mobile_interface():
    """Interface móvel otimizada"""
    return send_from_directory('.', 'mobile.html')

@app.route('/api/mobile/devices')
def api_mobile_devices():
    """API para descobrir dispositivos móveis"""
    if not ADVANCED_FEATURES or not mobile_manager:
        return jsonify({'success': False, 'error': 'Gerenciador móvel não disponível'}), 503
    
    try:
        # Descobrir dispositivos móveis na rede
        devices = mobile_manager.discover_mobile_devices("192.168.1.0/24")
        
        # Criar perfis detalhados
        device_profiles = []
        for device in devices:
            profile = mobile_manager.create_device_profile(device['device_info'])
            device_profiles.append(profile)
        
        return jsonify({
            'success': True,
            'devices': device_profiles,
            'count': len(device_profiles)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pentest/start', methods=['POST'])
def api_start_pentest():
    """API para iniciar teste de penetração"""
    if not ADVANCED_FEATURES or not pentest_system:
        return jsonify({'success': False, 'error': 'Sistema de pentest não disponível'}), 503
    
    try:
        data = request.get_json()
        target_network = data.get('network', '192.168.1.0/24')
        
        # Executar pentest em thread separada
        def run_pentest():
            results = pentest_system.comprehensive_scan(target_network)
            report = pentest_system.generate_pentest_report()
            
            # Emitir resultados
            socketio.emit('pentest_complete', {
                'results': results,
                'report': report,
                'timestamp': time.time()
            })
        
        pentest_thread = threading.Thread(target=run_pentest, daemon=True)
        pentest_thread.start()
        
        return jsonify({'success': True, 'message': 'Teste de penetração iniciado'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Eventos SocketIO
@socketio.on('connect')
def on_connect():
    global connected_clients
    connected_clients += 1
    print(f"Cliente conectado. Total: {connected_clients}")
    emit('system_status', system_status)

@socketio.on('disconnect')
def on_disconnect():
    global connected_clients
    connected_clients -= 1
    print(f"Cliente desconectado. Total: {connected_clients}")

@socketio.on('send_command')
def on_send_command(data):
    command = data.get('command', '')
    if command:
        print(f"Comando recebido: {command}")
        
        # Processar com IA avançada se disponível
        if ADVANCED_FEATURES and advanced_ai:
            try:
                ai_response = advanced_ai.generate_response(command)
                
                # Emitir resposta da IA avançada
                emit('ai_response', {
                    'response': ai_response,
                    'timestamp': time.time(),
                    'advanced': True,
                    'learning_active': True
                }, broadcast=True)
                
                return
            except Exception as e:
                print(f"Erro na IA avançada: {e}")
        
        # Resposta simples como fallback
        response = f"Processando comando: {command}"
        emit('ai_response', {
            'response': response,
            'timestamp': time.time(),
            'advanced': False
        }, broadcast=True)

@socketio.on('request_network_scan')
def on_request_network_scan():
    """Evento para solicitar scan de rede"""
    if ADVANCED_FEATURES and network_scanner:
        emit('network_scan_status', {'status': 'starting', 'message': 'Iniciando varredura de rede...'})
        
        def run_scan():
            try:
                results = network_scanner.full_network_scan()
                
                # Atualizar status do sistema
                system_status['network_devices'] = len(results)
                total_vulns = sum(len(data.get('vulnerabilities', [])) for data in results.values())
                system_status['vulnerabilities_found'] = total_vulns
                
                # Emitir resultados
                socketio.emit('network_scan_complete', {
                    'results': results,
                    'summary': {
                        'devices_found': len(results),
                        'vulnerabilities': total_vulns
                    },
                    'timestamp': time.time()
                })
            except Exception as e:
                socketio.emit('network_scan_error', {'error': str(e)})
        
        scan_thread = threading.Thread(target=run_scan, daemon=True)
        scan_thread.start()
    else:
        emit('network_scan_error', {'error': 'Scanner de rede não disponível'})

@socketio.on('request_mobile_scan')
def on_request_mobile_scan():
    """Evento para solicitar scan de dispositivos móveis"""
    if ADVANCED_FEATURES and mobile_manager:
        emit('mobile_scan_status', {'status': 'starting', 'message': 'Iniciando varredura de dispositivos móveis...'})
        
        def run_mobile_scan():
            try:
                devices = mobile_manager.discover_mobile_devices("192.168.1.0/24")
                
                device_profiles = []
                for device in devices:
                    profile = mobile_manager.create_device_profile(device['device_info'])
                    device_profiles.append(profile)
                
                # Emitir resultados
                socketio.emit('mobile_devices_found', {
                    'devices': device_profiles,
                    'count': len(device_profiles),
                    'timestamp': time.time()
                })
            except Exception as e:
                socketio.emit('mobile_scan_error', {'error': str(e)})
        
        mobile_scan_thread = threading.Thread(target=run_mobile_scan, daemon=True)
        mobile_scan_thread.start()
    else:
        emit('mobile_scan_error', {'error': 'Gerenciador móvel não disponível'})

@socketio.on('request_pentest')
def on_request_pentest(data):
    """Evento para solicitar teste de penetração"""
    if ADVANCED_FEATURES and pentest_system:
        target_network = data.get('network', '192.168.1.0/24')
        
        emit('pentest_status', {
            'status': 'starting', 
            'message': f'Iniciando teste de penetração em {target_network}...'
        })
        
        def run_pentest():
            try:
                results = pentest_system.comprehensive_scan(target_network)
                report = pentest_system.generate_pentest_report()
                
                # Emitir resultados
                socketio.emit('pentest_complete', {
                    'results': results,
                    'report': report,
                    'timestamp': time.time()
                })
            except Exception as e:
                socketio.emit('pentest_error', {'error': str(e)})
        
        pentest_thread = threading.Thread(target=run_pentest, daemon=True)
        pentest_thread.start()
    else:
        emit('pentest_error', {'error': 'Sistema de pentest não disponível'})

@socketio.on('control_device')
def on_control_device(data):
    device_id = data.get('device_id')
    action = data.get('action')
    
    print(f"Controle de dispositivo: {device_id} - {action}")
    
    # Emitir atualização
    emit('automation_update', {
        'device_id': device_id,
        'action': action,
        'timestamp': time.time()
    }, broadcast=True)

def main():
    """Função principal"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                  JARVIS Web Interface v1.0                       ║
    ║              Interface Web do Assistente JARVIS                  ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    print("🌐 Iniciando servidor web JARVIS...")
    print("📡 Servidor disponível em: http://localhost:5000")
    print("🔵 Pressione Ctrl+C para parar o servidor")
    
    try:
        socketio.run(
            app,
            host='localhost',
            port=5000,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n🔴 Servidor finalizado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    main()