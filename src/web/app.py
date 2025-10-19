#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Web do JARVIS
Dashboard de controle e monitoramento
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import json
import threading
import time
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.config_manager import ConfigManager
from core.logger import JarvisLogger, setup_logging
from core.events import EventManager, Events

class JarvisWebInterface:
    """Interface web para controle do JARVIS"""
    
    def __init__(self, config=None):
        if config is None:
            config_manager = ConfigManager()
            config = config_manager.load_config()
        
        self.config = config
        self.logger = JarvisLogger(__name__)
        
        # Configurações web
        web_config = config.get('web', {})
        self.host = web_config.get('host', 'localhost')
        self.port = web_config.get('port', 5000)
        self.debug = web_config.get('debug', False)
        
        # Criar app Flask
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = web_config.get('secret_key', 'jarvis-secret-key')
        
        # Configurar SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Event manager
        self.event_manager = EventManager.get_instance()
        
        # Estados
        self.connected_clients = 0
        self.system_status = {
            'online': False,
            'components': {},
            'last_update': time.time()
        }
        
        self._setup_routes()
        self._setup_socketio_events()
        self._setup_event_handlers()
        
        self.logger.system("Interface web inicializada")
    
    def _setup_routes(self):
        """Configura rotas HTTP"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
        
        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.system_status)
        
        @self.app.route('/api/devices')
        def api_devices():
            # Simular lista de dispositivos
            devices = [
                {'id': 'light_sala', 'name': 'Luz da Sala', 'type': 'light', 'state': False},
                {'id': 'light_quarto', 'name': 'Luz do Quarto', 'type': 'light', 'state': False},
                {'id': 'climate_main', 'name': 'Ar Condicionado', 'type': 'climate', 'state': 22}
            ]
            return jsonify(devices)
        
        @self.app.route('/api/command', methods=['POST'])
        def api_command():
            data = request.get_json()
            command = data.get('command', '')
            
            if command:
                # Emitir evento de comando
                self.event_manager.emit(Events.VOICE_COMMAND, {
                    'text': command,
                    'source': 'web_interface',
                    'timestamp': time.time()
                })
                return jsonify({'success': True, 'message': 'Comando enviado'})
            
            return jsonify({'success': False, 'message': 'Comando inválido'}), 400
        
        @self.app.route('/api/device/<device_id>/control', methods=['POST'])
        def api_device_control(device_id):
            data = request.get_json()
            action = data.get('action')
            value = data.get('value')
            
            # Emitir evento de automação
            self.event_manager.emit(Events.AUTOMATION_TRIGGERED, {
                'device_id': device_id,
                'action': action,
                'value': value,
                'source': 'web_interface'
            })
            
            return jsonify({'success': True, 'message': 'Comando de dispositivo enviado'})
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            return send_from_directory('static', filename)
    
    def _setup_socketio_events(self):
        """Configura eventos SocketIO"""
        
        @self.socketio.on('connect')
        def on_connect():
            self.connected_clients += 1
            self.logger.system(f"Cliente conectado. Total: {self.connected_clients}")
            emit('system_status', self.system_status)
        
        @self.socketio.on('disconnect')
        def on_disconnect():
            self.connected_clients -= 1
            self.logger.system(f"Cliente desconectado. Total: {self.connected_clients}")
        
        @self.socketio.on('send_command')
        def on_send_command(data):
            command = data.get('command', '')
            if command:
                self.event_manager.emit(Events.VOICE_COMMAND, {
                    'text': command,
                    'source': 'web_interface',
                    'timestamp': time.time()
                })
        
        @self.socketio.on('control_device')
        def on_control_device(data):
            device_id = data.get('device_id')
            action = data.get('action')
            value = data.get('value')
            
            self.event_manager.emit(Events.AUTOMATION_TRIGGERED, {
                'device_id': device_id,
                'action': action,
                'value': value,
                'source': 'web_interface'
            })
    
    def _setup_event_handlers(self):
        """Configura handlers de eventos do JARVIS"""
        
        self.event_manager.subscribe(Events.SYSTEM_STARTUP, self._on_system_startup)
        self.event_manager.subscribe(Events.SYSTEM_SHUTDOWN, self._on_system_shutdown)
        self.event_manager.subscribe(Events.AI_RESPONSE, self._on_ai_response)
        self.event_manager.subscribe(Events.VOICE_COMMAND, self._on_voice_command)
        self.event_manager.subscribe(Events.AUTOMATION_TRIGGERED, self._on_automation_triggered)
    
    def _on_system_startup(self, data):
        """Handler para startup do sistema"""
        self.system_status['online'] = True
        self.system_status['last_update'] = time.time()
        self._broadcast_system_update()
    
    def _on_system_shutdown(self, data):
        """Handler para shutdown do sistema"""
        self.system_status['online'] = False
        self.system_status['last_update'] = time.time()
        self._broadcast_system_update()
    
    def _on_ai_response(self, data):
        """Handler para respostas da IA"""
        if self.connected_clients > 0:
            self.socketio.emit('ai_response', {
                'response': data.get('text', ''),
                'command': data.get('command', ''),
                'timestamp': data.get('timestamp', time.time())
            })
    
    def _on_voice_command(self, data):
        """Handler para comandos de voz"""
        if self.connected_clients > 0 and data.get('source') != 'web_interface':
            self.socketio.emit('voice_command', {
                'command': data.get('text', ''),
                'timestamp': data.get('timestamp', time.time())
            })
    
    def _on_automation_triggered(self, data):
        """Handler para automações"""
        if self.connected_clients > 0:
            self.socketio.emit('automation_update', data)
    
    def _broadcast_system_update(self):
        """Transmite atualização do sistema para todos os clientes"""
        if self.connected_clients > 0:
            self.socketio.emit('system_status', self.system_status)
    
    def run(self, threaded=False):
        """Executa o servidor web"""
        if threaded:
            thread = threading.Thread(target=self._run_server)
            thread.daemon = True
            thread.start()
            return thread
        else:
            self._run_server()
    
    def _run_server(self):
        """Executa o servidor Flask"""
        self.logger.system(f"Iniciando servidor web em http://{self.host}:{self.port}")
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=self.debug
        )

# Templates HTML (serão salvos em arquivos separados)
def create_web_templates():
    """Cria templates HTML"""
    
    # Criar diretório de templates
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    os.makedirs(templates_dir, exist_ok=True)
    os.makedirs(static_dir, exist_ok=True)
    
    return templates_dir, static_dir

if __name__ == '__main__':
    # Configurar logging
    setup_logging()
    
    # Criar interface web
    web_interface = JarvisWebInterface()
    
    try:
        web_interface.run()
    except KeyboardInterrupt:
        print("\nInterface web finalizada")