#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Main Interface
Interface principal PyQt estilo Jarvis com efeitos visuais avançados
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPalette, QFont, QLinearGradient, QBrush, QColor
import time
from datetime import datetime

class AnimatedButton(QtWidgets.QPushButton):
    """Botão com animações personalizadas"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_glow)
        self.glow_intensity = 0
        self.glow_direction = 1
        
    def start_glow_animation(self):
        """Iniciar animação de brilho"""
        self.animation_timer.start(50)  # 50ms refresh
        
    def stop_glow_animation(self):
        """Parar animação de brilho"""
        self.animation_timer.stop()
        self.glow_intensity = 0
        self.update()
        
    def update_glow(self):
        """Atualizar intensidade do brilho"""
        self.glow_intensity += self.glow_direction * 5
        if self.glow_intensity >= 100:
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self.glow_direction = 1
        
        # Atualizar estilo com base na intensidade
        glow_color = f"rgba(79, 224, 255, {self.glow_intensity/100})"
        self.setStyleSheet(f"""
            QPushButton {{
                border-radius: 50px;
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #0fb4ff, stop:1 #00ffd1);
                color: #001;
                font-weight: bold;
                font-size: 16px;
                border: 2px solid {glow_color};
                box-shadow: 0 0 20px {glow_color};
            }}
            QPushButton:pressed {{
                transform: translateY(2px);
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #00a3e6, stop:1 #00e6b8);
            }}
        """)

class StatusIndicator(QtWidgets.QWidget):
    """Indicador de status com LED animado"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = "offline"  # offline, online, listening, processing
        self.setFixedSize(20, 20)
        
    def set_status(self, status):
        """Definir status: offline, online, listening, processing"""
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        """Desenhar indicador LED"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Cores baseadas no status
        colors = {
            'offline': '#666',
            'online': '#00ff00',
            'listening': '#4fe0ff',
            'processing': '#ff8c00'
        }
        
        color = colors.get(self.status, '#666')
        
        # Desenhar círculo LED
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QtGui.QPen(QColor('#fff'), 1))
        painter.drawEllipse(2, 2, 16, 16)
        
        # Efeito de brilho
        if self.status in ['listening', 'processing']:
            painter.setBrush(QBrush(QColor(color), Qt.Dense4Pattern))
            painter.drawEllipse(0, 0, 20, 20)

class NetworkVisualization(QtWidgets.QWidget):
    """Widget de visualização de rede"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []
        self.setMinimumHeight(150)
        
    def update_devices(self, devices):
        """Atualizar lista de dispositivos"""
        self.devices = devices
        self.update()
        
    def paintEvent(self, event):
        """Desenhar visualização de rede"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Fundo
        painter.fillRect(self.rect(), QColor('#0b0f14'))
        
        # Desenhar grid
        painter.setPen(QtGui.QPen(QColor('#073642'), 1))
        for i in range(0, self.width(), 30):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 30):
            painter.drawLine(0, i, self.width(), i)
        
        # Desenhar dispositivos
        if self.devices:
            device_spacing = self.width() // (len(self.devices) + 1)
            for i, device in enumerate(self.devices):
                x = device_spacing * (i + 1)
                y = self.height() // 2
                
                # Círculo do dispositivo
                painter.setBrush(QBrush(QColor('#4fe0ff')))
                painter.setPen(QtGui.QPen(QColor('#00ffd1'), 2))
                painter.drawEllipse(x-10, y-10, 20, 20)
                
                # Texto do IP
                painter.setPen(QtGui.QPen(QColor('#cfefff')))
                painter.setFont(QFont('Arial', 8))
                ip = device.get('ip', 'Unknown')
                painter.drawText(x-20, y+25, ip)

class JarvisUI(QtWidgets.QMainWindow):
    """Interface principal do JARVIS"""
    
    # Sinais
    command_requested = pyqtSignal()
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Atualizar a cada segundo
        
        self.setup_ui()
        self.apply_jarvis_style()
        
    def setup_ui(self):
        """Configurar interface do usuário"""
        self.setWindowTitle('JARVIS - Advanced AI Assistant')
        self.setMinimumSize(1200, 800)
        
        # Widget central
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        # Layout principal
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Painel esquerdo (principal)
        self.setup_left_panel(main_layout)
        
        # Painel direito (status e controles)
        self.setup_right_panel(main_layout)
        
        # Status bar
        self.setup_status_bar()
        
    def setup_left_panel(self, main_layout):
        """Configurar painel esquerdo"""
        left_panel = QtWidgets.QFrame()
        left_panel.setMinimumWidth(800)
        left_panel.setFrameStyle(QtWidgets.QFrame.Box)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        
        # Header com logo JARVIS
        header_frame = QtWidgets.QFrame()
        header_frame.setFixedHeight(80)
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        
        # Status LED
        self.status_led = StatusIndicator()
        self.status_led.set_status('online')
        header_layout.addWidget(self.status_led)
        
        # Logo JARVIS
        jarvis_label = QtWidgets.QLabel('J.A.R.V.I.S.')
        jarvis_label.setAlignment(Qt.AlignCenter)
        font = QFont('Arial', 32, QFont.Bold)
        jarvis_label.setFont(font)
        header_layout.addWidget(jarvis_label)
        
        # Subtítulo
        subtitle = QtWidgets.QLabel('Just A Rather Very Intelligent System')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont('Arial', 10))
        header_layout.addWidget(subtitle)
        
        left_layout.addWidget(header_frame)
        
        # Área de log/conversa
        self.log_area = QtWidgets.QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont('Consolas', 11))
        left_layout.addWidget(self.log_area)
        
        # Visualização de rede
        network_label = QtWidgets.QLabel('NETWORK VISUALIZATION')
        network_label.setAlignment(Qt.AlignCenter)
        network_label.setFont(QFont('Arial', 12, QFont.Bold))
        left_layout.addWidget(network_label)
        
        self.network_viz = NetworkVisualization()
        left_layout.addWidget(self.network_viz)
        
        # Controles principais
        controls_frame = QtWidgets.QFrame()
        controls_frame.setFixedHeight(120)
        controls_layout = QtWidgets.QHBoxLayout(controls_frame)
        
        # Botão de ouvir (principal)
        self.listen_btn = AnimatedButton('LISTEN')
        self.listen_btn.setFixedSize(100, 100)
        self.listen_btn.clicked.connect(self.on_listen_clicked)
        controls_layout.addWidget(self.listen_btn)
        
        # Botões secundários
        secondary_layout = QtWidgets.QVBoxLayout()
        
        self.scan_btn = QtWidgets.QPushButton('SCAN NETWORK')
        self.scan_btn.setFixedHeight(30)
        self.scan_btn.clicked.connect(self.on_scan_clicked)
        secondary_layout.addWidget(self.scan_btn)
        
        self.mobile_btn = QtWidgets.QPushButton('DETECT MOBILE')
        self.mobile_btn.setFixedHeight(30)
        self.mobile_btn.clicked.connect(self.on_mobile_clicked)
        secondary_layout.addWidget(self.mobile_btn)
        
        self.pentest_btn = QtWidgets.QPushButton('SECURITY SCAN')
        self.pentest_btn.setFixedHeight(30)
        self.pentest_btn.clicked.connect(self.on_pentest_clicked)
        secondary_layout.addWidget(self.pentest_btn)
        
        controls_layout.addLayout(secondary_layout)
        left_layout.addWidget(controls_frame)
        
        main_layout.addWidget(left_panel)
        
    def setup_right_panel(self, main_layout):
        """Configurar painel direito"""
        right_panel = QtWidgets.QFrame()
        right_panel.setMinimumWidth(350)
        right_panel.setMaximumWidth(400)
        right_panel.setFrameStyle(QtWidgets.QFrame.Box)
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        # Título do painel
        panel_title = QtWidgets.QLabel('SYSTEM STATUS')
        panel_title.setAlignment(Qt.AlignCenter)
        panel_title.setFont(QFont('Arial', 14, QFont.Bold))
        right_layout.addWidget(panel_title)
        
        # Lista de status
        self.status_list = QtWidgets.QListWidget()
        self.status_list.setFont(QFont('Consolas', 10))
        self.status_list.addItem('🎤 Microphone: Ready')
        self.status_list.addItem('🧠 AI Brain: Online')
        self.status_list.addItem('🌐 Network Scanner: Standby')
        self.status_list.addItem('📱 Mobile Detection: Standby')
        self.status_list.addItem('🔒 Security System: Armed')
        right_layout.addWidget(self.status_list)
        
        # Informações do sistema
        info_group = QtWidgets.QGroupBox('System Info')
        info_layout = QtWidgets.QVBoxLayout(info_group)
        
        self.uptime_label = QtWidgets.QLabel('Uptime: 00:00:00')
        self.memory_label = QtWidgets.QLabel('Memory: 0 MB')
        self.cpu_label = QtWidgets.QLabel('CPU: 0%')
        self.network_label = QtWidgets.QLabel('Network: Disconnected')
        
        for label in [self.uptime_label, self.memory_label, self.cpu_label, self.network_label]:
            label.setFont(QFont('Consolas', 9))
            info_layout.addWidget(label)
        
        right_layout.addWidget(info_group)
        
        # Controles avançados
        controls_group = QtWidgets.QGroupBox('Advanced Controls')
        controls_layout = QtWidgets.QVBoxLayout(controls_group)
        
        self.continuous_listen_cb = QtWidgets.QCheckBox('Continuous Listening')
        self.auto_scan_cb = QtWidgets.QCheckBox('Auto Network Scan')
        self.voice_feedback_cb = QtWidgets.QCheckBox('Voice Feedback')
        self.voice_feedback_cb.setChecked(True)
        
        for cb in [self.continuous_listen_cb, self.auto_scan_cb, self.voice_feedback_cb]:
            cb.setFont(QFont('Arial', 9))
            controls_layout.addWidget(cb)
        
        right_layout.addWidget(controls_group)
        
        main_layout.addWidget(right_panel)
        
    def setup_status_bar(self):
        """Configurar barra de status"""
        status_bar = self.statusBar()
        status_bar.setFont(QFont('Arial', 9))
        status_bar.showMessage('JARVIS Advanced Assistant - Ready')
        
    def apply_jarvis_style(self):
        """Aplicar estilo visual Jarvis"""
        style = """
        QMainWindow {
            background-color: #0b0f14;
            color: #cfefff;
        }
        
        QFrame {
            background-color: rgba(7, 16, 23, 0.8);
            border: 1px solid #073642;
            border-radius: 8px;
            margin: 2px;
        }
        
        QTextEdit {
            background-color: rgba(6, 10, 14, 0.9);
            border: 1px solid #073642;
            border-radius: 5px;
            padding: 10px;
            color: #cfefff;
            selection-background-color: #4fe0ff;
        }
        
        QListWidget {
            background-color: rgba(6, 10, 14, 0.9);
            border: 1px solid #073642;
            border-radius: 5px;
            color: #cfefff;
            alternate-background-color: rgba(79, 224, 255, 0.1);
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #073642;
        }
        
        QListWidget::item:selected {
            background-color: rgba(79, 224, 255, 0.3);
        }
        
        QPushButton {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #0fb4ff, stop:1 #00ffd1);
            color: #001;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 12px;
        }
        
        QPushButton:hover {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #4fe0ff, stop:1 #33ffd6);
        }
        
        QPushButton:pressed {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 #00a3e6, stop:1 #00e6b8);
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #4fe0ff;
            border-radius: 5px;
            margin: 5px;
            padding-top: 15px;
            color: #4fe0ff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
        }
        
        QCheckBox {
            spacing: 10px;
            color: #cfefff;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #4fe0ff;
            border-radius: 3px;
            background-color: transparent;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #4fe0ff;
            border-radius: 3px;
            background-color: #4fe0ff;
        }
        
        QLabel {
            color: #cfefff;
        }
        
        QStatusBar {
            background-color: #071017;
            border-top: 1px solid #073642;
            color: #cfefff;
        }
        """
        
        self.setStyleSheet(style)
        
        # Efeitos de sombra
        self.add_shadow_effects()
        
    def add_shadow_effects(self):
        """Adicionar efeitos de sombra"""
        # Sombra para o botão principal
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(79, 224, 255, 128))
        shadow.setOffset(0, 0)
        self.listen_btn.setGraphicsEffect(shadow)
        
    def on_listen_clicked(self):
        """Callback do botão de ouvir"""
        self.status_led.set_status('listening')
        self.listen_btn.start_glow_animation()
        self.append_log('🎤 Sistema ouvindo...', 'system')
        self.command_requested.emit()
        
        if self.controller:
            self.controller.start_listen()
            
    def on_scan_clicked(self):
        """Callback do botão de scan"""
        self.status_led.set_status('processing')
        self.append_log('🌐 Iniciando escaneamento de rede...', 'system')
        if self.controller:
            self.controller.start_network_scan()
            
    def on_mobile_clicked(self):
        """Callback do botão de detecção móvel"""
        self.status_led.set_status('processing')
        self.append_log('📱 Detectando dispositivos móveis...', 'system')
        if self.controller:
            self.controller.start_mobile_detection()
            
    def on_pentest_clicked(self):
        """Callback do botão de pentest"""
        self.status_led.set_status('processing')
        self.append_log('🔒 Iniciando análise de segurança...', 'system')
        if self.controller:
            self.controller.start_security_scan()
    
    def append_log(self, text, message_type='user'):
        """Adicionar texto ao log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Cores baseadas no tipo
        colors = {
            'user': '#4fe0ff',
            'assistant': '#00ffd1', 
            'system': '#ff8c00',
            'error': '#ff6b6b'
        }
        
        color = colors.get(message_type, '#cfefff')
        
        formatted_text = f'<span style="color: {color};">[{timestamp}] {text}</span>'
        self.log_area.append(formatted_text)
        
        # Scroll para o final
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_status_item(self, index, text):
        """Definir texto de item de status"""
        if 0 <= index < self.status_list.count():
            item = self.status_list.item(index)
            if item:
                item.setText(text)
    
    def update_status(self):
        """Atualizar informações de status"""
        # Atualizar uptime (placeholder)
        uptime = time.time() - getattr(self, '_start_time', time.time())
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        self.uptime_label.setText(f'Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}')
        
    def set_listening_state(self, listening):
        """Definir estado de escuta"""
        if listening:
            self.status_led.set_status('listening')
            self.listen_btn.start_glow_animation()
            self.set_status_item(0, '🎤 Microphone: Listening')
        else:
            self.status_led.set_status('online')
            self.listen_btn.stop_glow_animation()
            self.set_status_item(0, '🎤 Microphone: Ready')
    
    def set_processing_state(self, processing):
        """Definir estado de processamento"""
        if processing:
            self.status_led.set_status('processing')
            self.set_status_item(1, '🧠 AI Brain: Processing')
        else:
            self.status_led.set_status('online')
            self.set_status_item(1, '🧠 AI Brain: Online')
    
    def update_network_visualization(self, devices):
        """Atualizar visualização de rede"""
        self.network_viz.update_devices(devices)
        count = len(devices) if devices else 0
        self.set_status_item(2, f'🌐 Network Scanner: {count} devices found')
    
    def closeEvent(self, event):
        """Evento de fechamento"""
        self.append_log('🔴 Sistema JARVIS encerrando...', 'system')
        event.accept()
        
    def __del__(self):
        """Destrutor"""
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        if hasattr(self, 'listen_btn'):
            self.listen_btn.stop_glow_animation()