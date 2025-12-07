#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Main Application
Aplicação principal PyQt integrada com sistema avançado
"""

import sys
import os
import threading
import time
from pathlib import Path

# Adicionar diretórios ao path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))
sys.path.insert(0, str(project_dir.parent))

# Imports PyQt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, QTimer, pyqtSignal

# Imports locais
from qt_interface.interface.main_ui import JarvisUI
from qt_interface.core.listener import VoiceListener, listen_command
from qt_interface.core.responder import VoiceResponder, speak
from qt_interface.core.chatbot import ChatBot, get_response
from qt_interface.core.command_handler import CommandHandler, handle_command

class JarvisController(QtCore.QObject):
    """Controlador principal do JARVIS"""
    
    # Sinais
    log_message = pyqtSignal(str, str)  # text, type
    status_update = pyqtSignal(int, str)  # index, text
    listening_state = pyqtSignal(bool)
    processing_state = pyqtSignal(bool)
    network_devices_update = pyqtSignal(list)
    
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.start_time = time.time()
        
        # Inicializar componentes
        self.voice_listener = VoiceListener()
        self.voice_responder = VoiceResponder()
        self.chatbot = ChatBot()
        self.command_handler = CommandHandler()
        
        # Estado
        self.is_listening = False
        self.continuous_listening = False
        
        # Conectar sinais
        self.setup_signals()
        
        # Timer para auto-scan
        self.auto_scan_timer = QTimer()
        self.auto_scan_timer.timeout.connect(self.auto_network_scan)
        
        self.log_message.emit("✅ JARVIS Qt Controller initialized", "system")
        
    def setup_signals(self):
        """Configurar conexões de sinais"""
        # Conectar sinais internos à UI
        self.log_message.connect(self.ui.append_log)
        self.status_update.connect(self.ui.set_status_item)
        self.listening_state.connect(self.ui.set_listening_state)
        self.processing_state.connect(self.ui.set_processing_state)
        self.network_devices_update.connect(self.ui.update_network_visualization)
        
        # Conectar sinais do voice listener
        self.voice_listener.command_recognized.connect(self.process_voice_command)
        self.voice_listener.listening_started.connect(lambda: self.listening_state.emit(True))
        self.voice_listener.listening_stopped.connect(lambda: self.listening_state.emit(False))
        self.voice_listener.error_occurred.connect(self.handle_voice_error)
        
        # Conectar sinais do voice responder
        self.voice_responder.speech_started.connect(lambda text: self.log_message.emit(f"🔊 Falando: {text}", "assistant"))
        self.voice_responder.speech_finished.connect(lambda: self.processing_state.emit(False))
        self.voice_responder.speech_error.connect(self.handle_voice_error)
        
        # Conectar checkboxes da UI
        if hasattr(self.ui, 'continuous_listen_cb'):
            self.ui.continuous_listen_cb.toggled.connect(self.toggle_continuous_listening)
        if hasattr(self.ui, 'auto_scan_cb'):
            self.ui.auto_scan_cb.toggled.connect(self.toggle_auto_scan)
        if hasattr(self.ui, 'voice_feedback_cb'):
            self.ui.voice_feedback_cb.toggled.connect(self.toggle_voice_feedback)
    
    def start_listen(self):
        """Iniciar escuta de comando"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.listening_state.emit(True)
        self.log_message.emit("🎤 Iniciando escuta...", "system")
        
        # Usar thread para não bloquear UI
        threading.Thread(target=self._listen_thread, daemon=True).start()
    
    def _listen_thread(self):
        """Thread de escuta"""
        try:
            command = listen_command()
            if command:
                self.voice_listener.command_recognized.emit(command)
            else:
                self.log_message.emit("⚠️ Nenhum comando detectado", "system")
        except Exception as e:
            self.handle_voice_error(str(e))
        finally:
            self.is_listening = False
            self.listening_state.emit(False)
    
    def process_voice_command(self, command):
        """Processar comando de voz"""
        self.log_message.emit(f"👤 Usuário: {command}", "user")
        self.processing_state.emit(True)
        
        # Processar em thread separada
        threading.Thread(target=self._process_command_thread, args=(command,), daemon=True).start()
    
    def _process_command_thread(self, command):
        """Thread de processamento de comando"""
        try:
            # Primeiro, verificar comandos específicos
            simple_response = self.command_handler.handle_command(command)
            
            if simple_response:
                if simple_response == 'Encerrar':
                    self.log_message.emit("🔴 Comando de encerramento recebido", "system")
                    QtWidgets.QApplication.quit()
                    return
                
                self.log_message.emit(f"🤖 JARVIS: {simple_response}", "assistant")
                
                # Resposta de voz se habilitada
                if hasattr(self.ui, 'voice_feedback_cb') and self.ui.voice_feedback_cb.isChecked():
                    self.voice_responder.speak_async(simple_response)
                    
            else:
                # Usar IA para resposta mais complexa
                ai_response = self.chatbot.get_response(command)
                self.log_message.emit(f"🤖 JARVIS: {ai_response}", "assistant")
                
                # Resposta de voz se habilitada
                if hasattr(self.ui, 'voice_feedback_cb') and self.ui.voice_feedback_cb.isChecked():
                    self.voice_responder.speak_async(ai_response)
                    
        except Exception as e:
            error_msg = f"Erro ao processar comando: {e}"
            self.log_message.emit(error_msg, "error")
        finally:
            self.processing_state.emit(False)
            
            # Se escuta contínua estiver ativa, reiniciar
            if self.continuous_listening:
                time.sleep(1)  # Pequena pausa
                self.start_listen()
    
    def start_network_scan(self):
        """Iniciar escaneamento de rede"""
        self.log_message.emit("🌐 Executando escaneamento de rede...", "system")
        threading.Thread(target=self._network_scan_thread, daemon=True).start()
    
    def _network_scan_thread(self):
        """Thread de escaneamento de rede"""
        try:
            result = self.command_handler.execute_network_scan()
            if result.get('success'):
                devices = result.get('devices', [])
                count = result.get('count', 0)
                self.network_devices_update.emit(devices)
                self.log_message.emit(f"✅ Escaneamento concluído: {count} dispositivos encontrados", "system")
                self.status_update.emit(2, f"🌐 Network Scanner: {count} devices found")
            else:
                error = result.get('error', 'Erro desconhecido')
                self.log_message.emit(f"❌ Erro no escaneamento: {error}", "error")
        except Exception as e:
            self.log_message.emit(f"❌ Erro no escaneamento de rede: {e}", "error")
    
    def start_mobile_detection(self):
        """Iniciar detecção de dispositivos móveis"""
        self.log_message.emit("📱 Detectando dispositivos móveis...", "system")
        threading.Thread(target=self._mobile_detection_thread, daemon=True).start()
    
    def _mobile_detection_thread(self):
        """Thread de detecção móvel"""
        try:
            result = self.command_handler.execute_mobile_detection()
            if result.get('success'):
                devices = result.get('devices', [])
                count = result.get('count', 0)
                self.log_message.emit(f"✅ Detecção móvel concluída: {count} dispositivos encontrados", "system")
                self.status_update.emit(3, f"📱 Mobile Detection: {count} devices found")
            else:
                error = result.get('error', 'Erro desconhecido')
                self.log_message.emit(f"❌ Erro na detecção móvel: {error}", "error")
        except Exception as e:
            self.log_message.emit(f"❌ Erro na detecção móvel: {e}", "error")
    
    def start_security_scan(self):
        """Iniciar escaneamento de segurança"""
        self.log_message.emit("🔒 Iniciando análise de segurança...", "system")
        self.status_update.emit(4, "🔒 Security System: Scanning")
        
        # Simular scan de segurança (placeholder)
        def security_scan():
            time.sleep(3)
            self.log_message.emit("✅ Análise de segurança concluída", "system")
            self.status_update.emit(4, "🔒 Security System: Armed")
            
        threading.Thread(target=security_scan, daemon=True).start()
    
    def auto_network_scan(self):
        """Escaneamento automático de rede"""
        self.log_message.emit("🔄 Auto-scan de rede...", "system")
        self.start_network_scan()
    
    def toggle_continuous_listening(self, enabled):
        """Alternar escuta contínua"""
        self.continuous_listening = enabled
        if enabled:
            self.log_message.emit("🔄 Escuta contínua ativada", "system")
            if not self.is_listening:
                self.start_listen()
        else:
            self.log_message.emit("⏸️ Escuta contínua desativada", "system")
    
    def toggle_auto_scan(self, enabled):
        """Alternar auto-scan"""
        if enabled:
            self.auto_scan_timer.start(30000)  # 30 segundos
            self.log_message.emit("🔄 Auto-scan de rede ativado", "system")
        else:
            self.auto_scan_timer.stop()
            self.log_message.emit("⏸️ Auto-scan de rede desativado", "system")
    
    def toggle_voice_feedback(self, enabled):
        """Alternar feedback de voz"""
        if enabled:
            self.log_message.emit("🔊 Feedback de voz ativado", "system")
        else:
            self.log_message.emit("🔇 Feedback de voz desativado", "system")
    
    def handle_voice_error(self, error):
        """Manipular erros de voz"""
        self.log_message.emit(f"❌ Erro de voz: {error}", "error")
        self.listening_state.emit(False)
        self.processing_state.emit(False)

def main():
    """Função principal"""
    # Configurar aplicação
    app = QApplication(sys.argv)
    app.setApplicationName('JARVIS Advanced Assistant')
    app.setApplicationVersion('2.0')
    
    # Configurar estilo dark
    app.setStyle('Fusion')
    
    try:
        # Criar janela principal
        window = JarvisUI()
        
        # Criar controlador
        controller = JarvisController(window)
        window.controller = controller
        
        # Conectar sinal de comando da UI
        window.command_requested.connect(controller.start_listen)
        
        # Definir tempo de início
        window._start_time = time.time()
        
        # Mostrar janela
        window.show()
        
        # Mensagem inicial
        controller.log_message.emit("🚀 JARVIS Advanced Assistant iniciado", "system")
        controller.log_message.emit("💡 Use o botão LISTEN para comandos de voz", "system")
        controller.log_message.emit("🔧 Configure opções no painel lateral", "system")
        
        # Executar aplicação
        return app.exec_()
        
    except Exception as e:
        # Mostrar erro crítico
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('JARVIS - Erro Crítico')
        msg.setText(f'Erro ao inicializar JARVIS:\n\n{str(e)}')
        msg.exec_()
        return 1

if __name__ == '__main__':
    sys.exit(main())