#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Interface Principal Simplificada
"""

import sys
import json
import os

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, QMessageBox
    )
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    print("PyQt5 não disponível. Usando interface console.")
    PYQT_AVAILABLE = False

class JarvisSimpleWindow(QMainWindow):
    """Interface simplificada do JARVIS"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_theme()
        
        # Timer para atualização
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(30000)  # 30 segundos
    
    def init_ui(self):
        self.setWindowTitle("JARVIS Cyber Security System")
        self.setGeometry(200, 200, 900, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("J.A.R.V.I.S")
        title.setFont(QFont("Arial", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00d4ff; margin: 20px;")
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Cyber Security System")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Status
        self.status_label = QLabel("Sistema: Operacional")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #00ff00; font-weight: bold; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        # Input de alvo
        controls_layout.addWidget(QLabel("Alvo:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("IP ou hostname (ex: 127.0.0.1)")
        controls_layout.addWidget(self.target_input)
        
        # Botão de scan
        scan_btn = QPushButton("Scan Rápido")
        scan_btn.clicked.connect(self.quick_scan)
        controls_layout.addWidget(scan_btn)
        
        # Botão de hardening
        hardening_btn = QPushButton("Avaliar Segurança")
        hardening_btn.clicked.connect(self.run_hardening)
        controls_layout.addWidget(hardening_btn)
        
        layout.addLayout(controls_layout)
        
        # Área de resultados
        self.results_area = QTextEdit()
        self.results_area.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_area)
        
        # Log inicial
        self.log("Sistema JARVIS iniciado com sucesso!")
        self.log("Módulos carregados: Scanner, Firewall, Hardening")
        self.log("Aguardando comandos...")
    
    def apply_theme(self):
        """Aplicar tema JARVIS"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #00a8cc;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 2px solid #00d4ff;
                padding: 8px;
                border-radius: 4px;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #333333;
                color: #ffffff;
                padding: 10px;
            }
        """)
    
    def log(self, message: str):
        """Adicionar mensagem ao log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.results_area.append(log_entry)
        
        # Auto-scroll
        cursor = self.results_area.textCursor()
        cursor.movePosition(cursor.End)
        self.results_area.setTextCursor(cursor)
    
    def quick_scan(self):
        """Executar scan rápido"""
        target = self.target_input.text().strip()
        
        if not target:
            self.show_message("Erro", "Por favor, insira um alvo válido.")
            return
        
        self.log(f"Iniciando scan rápido em {target}...")
        
        try:
            # Importar e usar scanner
            from tools.simple_tools import run_quick_scan
            result = run_quick_scan(target)
            
            if 'error' in result:
                self.log(f"ERRO: {result['error']}")
            else:
                hosts = result.get('hosts', [])
                self.log(f"Scan concluído - {len(hosts)} hosts encontrados")
                
                for host in hosts[:3]:  # Mostrar apenas 3 primeiros
                    ip = host.get('ip', 'unknown')
                    ports = len(host.get('open_ports', []))
                    self.log(f"  {ip}: {ports} portas abertas")
                    
        except ImportError:
            self.log("ERRO: Módulo scanner não disponível")
        except Exception as e:
            self.log(f"ERRO: {str(e)}")
    
    def run_hardening(self):
        """Executar avaliação de segurança"""
        self.log("Executando avaliação de segurança do sistema...")
        
        try:
            from tools.simple_tools import run_quick_assessment
            assessment = run_quick_assessment()
            
            if 'error' in assessment:
                self.log(f"ERRO: {assessment['error']}")
            else:
                score = assessment.get('overall_score', 0)
                self.log(f"Avaliação concluída - Score: {score}/100")
                
                if score >= 80:
                    self.log("Status: Sistema bem protegido! ✅")
                elif score >= 60:
                    self.log("Status: Sistema parcialmente protegido ⚠️")
                else:
                    self.log("Status: Sistema precisa de melhorias ❌")
                
                recommendations = assessment.get('recommendations', [])
                if recommendations:
                    self.log("Principais recomendações:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        self.log(f"  {i}. {rec}")
                        
        except ImportError:
            self.log("ERRO: Módulo hardening não disponível")
        except Exception as e:
            self.log(f"ERRO: {str(e)}")
    
    def update_status(self):
        """Atualizar status do sistema"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_label.setText(f"Sistema: Operacional - {current_time}")
    
    def show_message(self, title: str, message: str):
        """Mostrar mensagem"""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
    
    def closeEvent(self, event):
        """Evento de fechamento"""
        self.log("Encerrando JARVIS Cyber Security System...")
        event.accept()

def main():
    """Função principal"""
    if not PYQT_AVAILABLE:
        print("PyQt5 não está disponível.")
        print("Instale com: pip install PyQt5")
        return
    
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS Cyber Security")
    
    # Criar e mostrar janela
    window = JarvisSimpleWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()