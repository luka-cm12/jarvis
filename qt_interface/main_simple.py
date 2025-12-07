#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Simple Main
Versão simplificada do JARVIS PyQt
"""

import sys
import os
import json
import threading
import time
from pathlib import Path

# Imports PyQt
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QObject
except ImportError:
    print("❌ PyQt5 não encontrado. Execute: pip install PyQt5")
    sys.exit(1)

# Imports de voz
try:
    import speech_recognition as sr
    import pyttsx3
except ImportError:
    print("❌ Bibliotecas de voz não encontradas. Execute: pip install SpeechRecognition pyttsx3")
    speech_recognition = None
    pyttsx3 = None

class SimpleJarvisUI(QMainWindow):
    """Interface JARVIS simplificada"""
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.setup_ui()
        self.setup_voice()
        
    def load_config(self):
        """Carregar configurações"""
        config_file = Path(__file__).parent / "config" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Configuração padrão
        return {
            "voice": {"language": "pt-BR", "rate": 150, "volume": 1.0},
            "ui": {"theme_color": "#4fe0ff", "accent_color": "#00ffd1", 
                   "background_color": "#0b0f14", "text_color": "#cfefff"}
        }
    
    def setup_ui(self):
        """Configurar interface"""
        self.setWindowTitle('JARVIS - Simple PyQt Interface')
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        layout = QtWidgets.QVBoxLayout(central)
        
        # Header
        header = QtWidgets.QLabel('J.A.R.V.I.S.')
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setFont(QtGui.QFont('Arial', 36, QtGui.QFont.Bold))
        layout.addWidget(header)
        
        subtitle = QtWidgets.QLabel('Just A Rather Very Intelligent System')
        subtitle.setAlignment(QtCore.Qt.AlignCenter)
        subtitle.setFont(QtGui.QFont('Arial', 12))
        layout.addWidget(subtitle)
        
        # Log area
        self.log_area = QtWidgets.QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QtGui.QFont('Consolas', 11))
        layout.addWidget(self.log_area)
        
        # Controles
        controls = QtWidgets.QHBoxLayout()
        
        self.listen_btn = QtWidgets.QPushButton('🎤 OUVIR')
        self.listen_btn.setFixedSize(120, 60)
        self.listen_btn.setFont(QtGui.QFont('Arial', 12, QtGui.QFont.Bold))
        self.listen_btn.clicked.connect(self.start_listening)
        controls.addWidget(self.listen_btn)
        
        self.clear_btn = QtWidgets.QPushButton('🗑️ LIMPAR')
        self.clear_btn.setFixedSize(120, 60)
        self.clear_btn.setFont(QtGui.QFont('Arial', 12, QtGui.QFont.Bold))
        self.clear_btn.clicked.connect(self.clear_log)
        controls.addWidget(self.clear_btn)
        
        layout.addLayout(controls)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('JARVIS Ready - PyQt Simple Version')
        
        # Aplicar estilo
        self.apply_style()
        
        # Log inicial
        self.add_log("🤖 JARVIS Simple PyQt Interface iniciado", "system")
        if speech_recognition and pyttsx3:
            self.add_log("✅ Sistema de voz carregado", "system")
        else:
            self.add_log("⚠️ Sistema de voz não disponível", "warning")
        
    def setup_voice(self):
        """Configurar sistema de voz"""
        self.recognizer = None
        self.tts_engine = None
        
        if speech_recognition:
            self.recognizer = sr.Recognizer()
            
        if pyttsx3:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.config.get('voice', {}).get('rate', 150))
                self.tts_engine.setProperty('volume', self.config.get('voice', {}).get('volume', 1.0))
            except:
                self.tts_engine = None
    
    def apply_style(self):
        """Aplicar estilo Jarvis"""
        theme = self.config.get('ui', {})
        theme_color = theme.get('theme_color', '#4fe0ff')
        accent_color = theme.get('accent_color', '#00ffd1')
        bg_color = theme.get('background_color', '#0b0f14')
        text_color = theme.get('text_color', '#cfefff')
        
        style = f"""
        QMainWindow {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        QLabel {{
            color: {theme_color};
        }}
        
        QTextEdit {{
            background-color: rgba(6, 10, 14, 0.9);
            border: 2px solid {theme_color};
            border-radius: 8px;
            padding: 10px;
            color: {text_color};
            font-size: 12px;
        }}
        
        QPushButton {{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {theme_color}, stop:1 {accent_color});
            color: #001;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 10px;
        }}
        
        QPushButton:hover {{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {accent_color}, stop:1 {theme_color});
        }}
        
        QPushButton:pressed {{
            background-color: rgba(79, 224, 255, 0.7);
        }}
        
        QStatusBar {{
            background-color: rgba(7, 16, 23, 0.9);
            border-top: 1px solid {theme_color};
            color: {text_color};
        }}
        """
        
        self.setStyleSheet(style)
    
    def add_log(self, message, msg_type="info"):
        """Adicionar mensagem ao log"""
        timestamp = time.strftime('%H:%M:%S')
        
        colors = {
            "system": "#4fe0ff",
            "user": "#00ffd1", 
            "assistant": "#ffff00",
            "warning": "#ff8c00",
            "error": "#ff6b6b"
        }
        
        color = colors.get(msg_type, "#cfefff")
        formatted = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        
        self.log_area.append(formatted)
        
        # Scroll para o final
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Limpar log"""
        self.log_area.clear()
        self.add_log("🗑️ Log limpo", "system")
    
    def start_listening(self):
        """Iniciar escuta"""
        if not self.recognizer:
            self.add_log("❌ Sistema de reconhecimento de voz não disponível", "error")
            return
            
        self.listen_btn.setEnabled(False)
        self.listen_btn.setText('🎤 OUVINDO...')
        self.status_bar.showMessage('Ouvindo comando...')
        
        # Usar thread para não bloquear UI
        threading.Thread(target=self._listen_thread, daemon=True).start()
    
    def _listen_thread(self):
        """Thread de escuta"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Callback para UI thread
                QtCore.QMetaObject.invokeMethod(
                    self, "_update_listening_ui",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, "Ouvindo...")
                )
                
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.config.get('voice', {}).get('language', 'pt-BR')
                )
                
                # Callback para processar comando
                QtCore.QMetaObject.invokeMethod(
                    self, "_process_command",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, text)
                )
                
        except sr.WaitTimeoutError:
            QtCore.QMetaObject.invokeMethod(
                self, "_handle_listen_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, "Timeout: Nenhum comando detectado")
            )
        except sr.UnknownValueError:
            QtCore.QMetaObject.invokeMethod(
                self, "_handle_listen_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, "Não foi possível entender o áudio")
            )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self, "_handle_listen_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"Erro: {str(e)}")
            )
    
    @QtCore.pyqtSlot(str)
    def _update_listening_ui(self, message):
        """Atualizar UI durante escuta"""
        self.add_log(f"🎤 {message}", "system")
    
    @QtCore.pyqtSlot(str)
    def _process_command(self, command):
        """Processar comando reconhecido"""
        self.add_log(f"👤 Usuário: {command}", "user")
        
        # Processar comando
        response = self.handle_command(command.lower())
        
        if response:
            if response == "SAIR":
                self.close()
                return
            
            self.add_log(f"🤖 JARVIS: {response}", "assistant")
            
            # Falar resposta se TTS disponível
            if self.tts_engine:
                threading.Thread(target=self._speak, args=(response,), daemon=True).start()
        
        # Restaurar botão
        self._reset_listen_button()
    
    @QtCore.pyqtSlot(str)
    def _handle_listen_error(self, error):
        """Lidar com erro de escuta"""
        self.add_log(f"❌ {error}", "error")
        self._reset_listen_button()
    
    def _reset_listen_button(self):
        """Restaurar botão de escuta"""
        self.listen_btn.setEnabled(True)
        self.listen_btn.setText('🎤 OUVIR')
        self.status_bar.showMessage('JARVIS Ready')
    
    def _speak(self, text):
        """Falar texto"""
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except:
                pass
    
    def handle_command(self, command):
        """Processar comando simples"""
        import webbrowser
        from datetime import datetime
        
        if any(word in command for word in ['sair', 'fechar', 'encerrar']):
            return "SAIR"
        
        if any(word in command for word in ['horas', 'horário']):
            now = datetime.now()
            return f"São {now.strftime('%H:%M')} de {now.strftime('%d/%m/%Y')}"
        
        if 'youtube' in command:
            webbrowser.open('https://www.youtube.com')
            return "Abrindo YouTube"
        
        if 'spotify' in command or 'música' in command:
            webbrowser.open('https://open.spotify.com')
            return "Abrindo Spotify"
        
        if 'google' in command:
            webbrowser.open('https://www.google.com')
            return "Abrindo Google"
        
        if any(word in command for word in ['olá', 'oi', 'hey']):
            return "Olá! Como posso ajudá-lo?"
        
        if 'jarvis' in command:
            return "Sim senhor, estou aqui para ajudar."
        
        # Resposta padrão
        responses = [
            "Comando reconhecido, mas não implementado ainda.",
            "Interessante. Vou processar essa informação.",
            "Entendi. Há algo mais que posso fazer?",
            "Comando registrado no sistema.",
            "Processando solicitação..."
        ]
        
        import random
        return random.choice(responses)

def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    # Configurar aplicação
    app.setApplicationName('JARVIS Simple PyQt')
    app.setApplicationVersion('1.0')
    
    # Estilo dark
    app.setStyle('Fusion')
    
    try:
        # Criar e mostrar janela
        window = SimpleJarvisUI()
        window.show()
        
        # Executar aplicação
        return app.exec_()
        
    except Exception as e:
        # Mostrar erro
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle('JARVIS - Erro')
        msg.setText(f'Erro ao inicializar:\n\n{str(e)}')
        msg.exec_()
        return 1

if __name__ == '__main__':
    sys.exit(main())