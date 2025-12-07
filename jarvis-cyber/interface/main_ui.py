#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Main Interface
Interface principal para operações de cibersegurança com PyQt5
"""

import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QProgressBar, QCheckBox,
    QScrollArea, QSplitter, QFrame, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

# Importar módulos JARVIS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from tools.scanner import SecureScanner, run_quick_scan
    from tools.firewall import FirewallManager, check_firewall_status
    from tools.hardening import SystemHardening, run_quick_assessment
    from server.auth import generate_agent_credentials
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")

class ScannerThread(QThread):
    """Thread para executar scans sem bloquear UI"""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, scan_type: str, target: str, options: Dict = None):
        super().__init__()
        self.scan_type = scan_type
        self.target = target
        self.options = options or {}
    
    def run(self):
        try:
            self.progress.emit(f"Iniciando {self.scan_type} em {self.target}")
            
            scanner = SecureScanner()
            
            if self.scan_type == "quick":
                result = scanner.scan_ports_quick(self.target)
            elif self.scan_type == "full":
                port_range = self.options.get('port_range', '1-1000')
                result = scanner.scan_ports_full(self.target, port_range)
            elif self.scan_type == "vulnerability":
                result = scanner.scan_vulnerabilities(self.target)
            elif self.scan_type == "basic":
                result = scanner.scan_host_basic(self.target)
            else:
                result = {"error": f"Tipo de scan desconhecido: {self.scan_type}"}
            
            self.finished.emit(result)
            
        except Exception as e:
            self.finished.emit({"error": str(e)})

class HardeningThread(QThread):
    """Thread para hardening de sistema"""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
    
    def run(self):
        try:
            self.progress.emit("Executando avaliação de segurança...")
            
            hardening = SystemHardening()
            result = hardening.run_security_assessment()
            
            self.finished.emit(result)
            
        except Exception as e:
            self.finished.emit({"error": str(e)})

class JarvisMainWindow(QMainWindow):
    """Interface principal JARVIS"""
    
    def __init__(self):
        super().__init__()
        self.scanner = SecureScanner()
        self.firewall_manager = FirewallManager()
        self.hardening = SystemHardening()
        
        self.scan_history = []
        
        self.init_ui()
        self.apply_jarvis_theme()
        
        # Timer para atualizações
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(30000)  # 30 segundos
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        self.setWindowTitle("JARVIS Cyber Security System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tabs principais
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Criar abas
        self.create_scanner_tab()
        self.create_firewall_tab()
        self.create_hardening_tab()
        self.create_logs_tab()
        self.create_agents_tab()
        
        # Status bar
        self.statusBar().showMessage("JARVIS Cyber Security System - Pronto")
    
    def create_header(self) -> QWidget:
        """Criar header com informações do sistema"""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 #1a1a2e, stop:1 #16213e);"
        )
        
        layout = QHBoxLayout(header_frame)
        
        # Logo/Título
        title_label = QLabel("J.A.R.V.I.S")
        title_label.setFont(QFont("Arial", 28, QFont.Bold))
        title_label.setStyleSheet("color: #00d4ff; margin: 10px;")\n        layout.addWidget(title_label)\n        \n        # Subtítulo\n        subtitle_label = QLabel(\"Cyber Security System\")\n        subtitle_label.setFont(QFont(\"Arial\", 12))\n        subtitle_label.setStyleSheet(\"color: #ffffff; margin-top: 30px;\")\n        layout.addWidget(subtitle_label)\n        \n        layout.addStretch()\n        \n        # Status do sistema\n        self.system_status = QLabel(\"Sistema: Operacional\")\n        self.system_status.setStyleSheet(\"color: #00ff00; font-weight: bold;\")\n        layout.addWidget(self.system_status)\n        \n        return header_frame\n    \n    def create_scanner_tab(self):\n        \"\"\"Criar aba do scanner\"\"\"\n        scanner_widget = QWidget()\n        layout = QVBoxLayout(scanner_widget)\n        \n        # Controles de scan\n        controls_group = QGroupBox(\"Controles de Scanner\")\n        controls_layout = QHBoxLayout(controls_group)\n        \n        # Campo de alvo\n        controls_layout.addWidget(QLabel(\"Alvo:\"))\n        self.target_input = QLineEdit()\n        self.target_input.setPlaceholderText(\"IP, hostname ou CIDR (ex: 192.168.1.0/24)\")\n        controls_layout.addWidget(self.target_input)\n        \n        # Tipo de scan\n        controls_layout.addWidget(QLabel(\"Tipo:\"))\n        self.scan_type_combo = QComboBox()\n        self.scan_type_combo.addItems([\"Quick Scan\", \"Full Scan\", \"Vulnerability Scan\", \"Basic Scan\"])\n        controls_layout.addWidget(self.scan_type_combo)\n        \n        # Botão de scan\n        self.scan_button = QPushButton(\"Iniciar Scan\")\n        self.scan_button.clicked.connect(self.start_scan)\n        controls_layout.addWidget(self.scan_button)\n        \n        layout.addWidget(controls_group)\n        \n        # Área de progresso\n        self.scan_progress = QProgressBar()\n        self.scan_progress.setVisible(False)\n        layout.addWidget(self.scan_progress)\n        \n        # Resultados\n        self.scan_results = QTextEdit()\n        self.scan_results.setFont(QFont(\"Consolas\", 10))\n        layout.addWidget(self.scan_results)\n        \n        self.tab_widget.addTab(scanner_widget, \"Scanner\")\n    \n    def create_firewall_tab(self):\n        \"\"\"Criar aba do firewall\"\"\"\n        firewall_widget = QWidget()\n        layout = QVBoxLayout(firewall_widget)\n        \n        # Status do firewall\n        status_group = QGroupBox(\"Status do Firewall\")\n        status_layout = QVBoxLayout(status_group)\n        \n        self.firewall_status = QTextEdit()\n        self.firewall_status.setMaximumHeight(150)\n        status_layout.addWidget(self.firewall_status)\n        \n        # Botão para verificar status\n        check_status_btn = QPushButton(\"Verificar Status\")\n        check_status_btn.clicked.connect(self.check_firewall_status)\n        status_layout.addWidget(check_status_btn)\n        \n        layout.addWidget(status_group)\n        \n        # Controles do firewall\n        controls_group = QGroupBox(\"Controles de Hardening\")\n        controls_layout = QVBoxLayout(controls_group)\n        \n        # Opções de hardening\n        self.dry_run_checkbox = QCheckBox(\"Modo dry-run (apenas simular)\")\n        self.dry_run_checkbox.setChecked(True)\n        controls_layout.addWidget(self.dry_run_checkbox)\n        \n        # Botões\n        buttons_layout = QHBoxLayout()\n        \n        apply_hardening_btn = QPushButton(\"Aplicar Hardening Básico\")\n        apply_hardening_btn.clicked.connect(self.apply_firewall_hardening)\n        buttons_layout.addWidget(apply_hardening_btn)\n        \n        backup_btn = QPushButton(\"Fazer Backup\")\n        backup_btn.clicked.connect(self.backup_firewall)\n        buttons_layout.addWidget(backup_btn)\n        \n        controls_layout.addLayout(buttons_layout)\n        \n        layout.addWidget(controls_group)\n        \n        # Logs de firewall\n        logs_group = QGroupBox(\"Logs e Resultados\")\n        logs_layout = QVBoxLayout(logs_group)\n        \n        self.firewall_logs = QTextEdit()\n        self.firewall_logs.setFont(QFont(\"Consolas\", 10))\n        logs_layout.addWidget(self.firewall_logs)\n        \n        layout.addWidget(logs_group)\n        \n        self.tab_widget.addTab(firewall_widget, \"Firewall\")\n    \n    def create_hardening_tab(self):\n        \"\"\"Criar aba de hardening\"\"\"\n        hardening_widget = QWidget()\n        layout = QVBoxLayout(hardening_widget)\n        \n        # Controles\n        controls_group = QGroupBox(\"Avaliação de Segurança\")\n        controls_layout = QHBoxLayout(controls_group)\n        \n        assess_btn = QPushButton(\"Executar Avaliação\")\n        assess_btn.clicked.connect(self.run_security_assessment)\n        controls_layout.addWidget(assess_btn)\n        \n        # Score de segurança\n        self.security_score = QLabel(\"Score: --/100\")\n        self.security_score.setFont(QFont(\"Arial\", 14, QFont.Bold))\n        controls_layout.addWidget(self.security_score)\n        \n        controls_layout.addStretch()\n        layout.addWidget(controls_group)\n        \n        # Resultados em duas colunas\n        results_splitter = QSplitter(Qt.Horizontal)\n        \n        # Checks de segurança\n        checks_group = QGroupBox(\"Checks de Segurança\")\n        checks_layout = QVBoxLayout(checks_group)\n        \n        self.security_checks = QTableWidget()\n        self.security_checks.setColumnCount(3)\n        self.security_checks.setHorizontalHeaderLabels([\"Check\", \"Status\", \"Detalhes\"])\n        checks_layout.addWidget(self.security_checks)\n        \n        results_splitter.addWidget(checks_group)\n        \n        # Recomendações\n        recommendations_group = QGroupBox(\"Recomendações\")\n        recommendations_layout = QVBoxLayout(recommendations_group)\n        \n        self.recommendations_list = QTextEdit()\n        self.recommendations_list.setFont(QFont(\"Arial\", 10))\n        recommendations_layout.addWidget(self.recommendations_list)\n        \n        results_splitter.addWidget(recommendations_group)\n        \n        layout.addWidget(results_splitter)\n        \n        self.tab_widget.addTab(hardening_widget, \"Hardening\")\n    \n    def create_logs_tab(self):\n        \"\"\"Criar aba de logs\"\"\"\n        logs_widget = QWidget()\n        layout = QVBoxLayout(logs_widget)\n        \n        # Filtros\n        filter_group = QGroupBox(\"Filtros\")\n        filter_layout = QHBoxLayout(filter_group)\n        \n        filter_layout.addWidget(QLabel(\"Tipo:\"))\n        self.log_type_filter = QComboBox()\n        self.log_type_filter.addItems([\"Todos\", \"Scanner\", \"Firewall\", \"Hardening\", \"Sistema\"])\n        filter_layout.addWidget(self.log_type_filter)\n        \n        clear_logs_btn = QPushButton(\"Limpar Logs\")\n        clear_logs_btn.clicked.connect(self.clear_logs)\n        filter_layout.addWidget(clear_logs_btn)\n        \n        filter_layout.addStretch()\n        layout.addWidget(filter_group)\n        \n        # Área de logs\n        self.logs_display = QTextEdit()\n        self.logs_display.setFont(QFont(\"Consolas\", 9))\n        self.logs_display.setReadOnly(True)\n        layout.addWidget(self.logs_display)\n        \n        self.tab_widget.addTab(logs_widget, \"Logs\")\n    \n    def create_agents_tab(self):\n        \"\"\"Criar aba de agentes\"\"\"\n        agents_widget = QWidget()\n        layout = QVBoxLayout(agents_widget)\n        \n        # Controles de agentes\n        controls_group = QGroupBox(\"Gerenciamento de Agentes\")\n        controls_layout = QHBoxLayout(controls_group)\n        \n        create_agent_btn = QPushButton(\"Criar Novo Agente\")\n        create_agent_btn.clicked.connect(self.create_new_agent)\n        controls_layout.addWidget(create_agent_btn)\n        \n        refresh_agents_btn = QPushButton(\"Atualizar Lista\")\n        refresh_agents_btn.clicked.connect(self.refresh_agents)\n        controls_layout.addWidget(refresh_agents_btn)\n        \n        controls_layout.addStretch()\n        layout.addWidget(controls_group)\n        \n        # Lista de agentes\n        self.agents_table = QTableWidget()\n        self.agents_table.setColumnCount(5)\n        self.agents_table.setHorizontalHeaderLabels([\"ID\", \"Nome\", \"Status\", \"Último Ping\", \"Ações\"])\n        layout.addWidget(self.agents_table)\n        \n        self.tab_widget.addTab(agents_widget, \"Agentes\")\n    \n    def apply_jarvis_theme(self):\n        \"\"\"Aplicar tema JARVIS\"\"\"\n        self.setStyleSheet(\"\"\"\n            QMainWindow {\n                background-color: #0a0a0a;\n                color: #ffffff;\n            }\n            \n            QTabWidget::pane {\n                border: 1px solid #00d4ff;\n                background-color: #1a1a1a;\n            }\n            \n            QTabBar::tab {\n                background-color: #2a2a2a;\n                color: #ffffff;\n                padding: 8px 16px;\n                border: 1px solid #444444;\n                border-bottom: none;\n            }\n            \n            QTabBar::tab:selected {\n                background-color: #00d4ff;\n                color: #000000;\n                font-weight: bold;\n            }\n            \n            QGroupBox {\n                color: #00d4ff;\n                font-weight: bold;\n                border: 2px solid #00d4ff;\n                border-radius: 5px;\n                margin-top: 10px;\n                padding-top: 10px;\n            }\n            \n            QGroupBox::title {\n                subcontrol-origin: margin;\n                left: 10px;\n                padding: 0 5px 0 5px;\n            }\n            \n            QPushButton {\n                background-color: #00d4ff;\n                color: #000000;\n                border: none;\n                padding: 8px 16px;\n                border-radius: 4px;\n                font-weight: bold;\n            }\n            \n            QPushButton:hover {\n                background-color: #00a8cc;\n            }\n            \n            QPushButton:pressed {\n                background-color: #007799;\n            }\n            \n            QLineEdit, QComboBox {\n                background-color: #2a2a2a;\n                border: 1px solid #00d4ff;\n                padding: 5px;\n                border-radius: 3px;\n                color: #ffffff;\n            }\n            \n            QTextEdit {\n                background-color: #1a1a1a;\n                border: 1px solid #333333;\n                color: #ffffff;\n            }\n            \n            QTableWidget {\n                background-color: #1a1a1a;\n                gridline-color: #333333;\n                color: #ffffff;\n            }\n            \n            QHeaderView::section {\n                background-color: #00d4ff;\n                color: #000000;\n                font-weight: bold;\n                padding: 5px;\n                border: none;\n            }\n            \n            QProgressBar {\n                border: 1px solid #333333;\n                border-radius: 5px;\n                text-align: center;\n            }\n            \n            QProgressBar::chunk {\n                background-color: #00d4ff;\n                border-radius: 5px;\n            }\n            \n            QStatusBar {\n                background-color: #1a1a1a;\n                color: #00d4ff;\n            }\n        \"\"\")\n    \n    def start_scan(self):\n        \"\"\"Iniciar scan\"\"\"\n        target = self.target_input.text().strip()\n        if not target:\n            self.show_message(\"Erro\", \"Por favor, insira um alvo para o scan.\")\n            return\n        \n        # Validar alvo\n        is_valid, error = self.scanner.validate_target(target)\n        if not is_valid:\n            self.show_message(\"Erro de Validação\", error)\n            return\n        \n        # Determinar tipo de scan\n        scan_type_map = {\n            \"Quick Scan\": \"quick\",\n            \"Full Scan\": \"full\",\n            \"Vulnerability Scan\": \"vulnerability\",\n            \"Basic Scan\": \"basic\"\n        }\n        \n        scan_type = scan_type_map.get(self.scan_type_combo.currentText(), \"quick\")\n        \n        # Desabilitar botão e mostrar progresso\n        self.scan_button.setEnabled(False)\n        self.scan_progress.setVisible(True)\n        self.scan_progress.setRange(0, 0)  # Indeterminate progress\n        \n        # Iniciar thread de scan\n        self.scanner_thread = ScannerThread(scan_type, target)\n        self.scanner_thread.finished.connect(self.on_scan_finished)\n        self.scanner_thread.progress.connect(self.update_scan_progress)\n        self.scanner_thread.start()\n        \n        self.log_message(\"Scanner\", f\"Iniciando {scan_type} scan em {target}\")\n    \n    def on_scan_finished(self, result: Dict[str, Any]):\n        \"\"\"Processar resultado do scan\"\"\"\n        self.scan_button.setEnabled(True)\n        self.scan_progress.setVisible(False)\n        \n        if \"error\" in result:\n            self.scan_results.setText(f\"Erro no scan: {result['error']}\")\n            self.log_message(\"Scanner\", f\"Erro: {result['error']}\", \"error\")\n        else:\n            # Formatar resultado\n            formatted_result = self.format_scan_result(result)\n            self.scan_results.setText(formatted_result)\n            \n            # Adicionar ao histórico\n            self.scan_history.append(result)\n            \n            self.log_message(\"Scanner\", f\"Scan concluído: {result.get('scan_type', 'unknown')}\")\n    \n    def update_scan_progress(self, message: str):\n        \"\"\"Atualizar progresso do scan\"\"\"\n        self.statusBar().showMessage(message)\n    \n    def format_scan_result(self, result: Dict[str, Any]) -> str:\n        \"\"\"Formatar resultado do scan para exibição\"\"\"\n        formatted = f\"=== RESULTADO DO SCAN ===\\n\"\n        formatted += f\"Tipo: {result.get('scan_type', 'unknown')}\\n\"\n        formatted += f\"Alvo: {result.get('target', 'unknown')}\\n\"\n        formatted += f\"Timestamp: {datetime.fromtimestamp(result.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}\\n\\n\"\n        \n        if \"hosts\" in result:\n            formatted += f\"Hosts encontrados: {len(result['hosts'])}\\n\\n\"\n            \n            for host in result[\"hosts\"]:\n                formatted += f\"Host: {host.get('ip', 'unknown')}\\n\"\n                \n                if \"hostname\" in host and host[\"hostname\"]:\n                    formatted += f\"  Hostname: {host['hostname']}\\n\"\n                \n                if \"open_ports\" in host:\n                    formatted += f\"  Portas abertas: {len(host['open_ports'])}\\n\"\n                    for port in host[\"open_ports\"][:10]:  # Mostrar apenas primeiras 10\n                        formatted += f\"    {port['port']}/{port.get('service', 'unknown')}\\n\"\n                \n                formatted += \"\\n\"\n        \n        if \"vulnerabilities\" in result:\n            formatted += f\"Vulnerabilidades encontradas: {len(result['vulnerabilities'])}\\n\\n\"\n            \n            for vuln in result[\"vulnerabilities\"][:5]:  # Mostrar apenas primeiras 5\n                formatted += f\"Host: {vuln.get('host', 'unknown')}:{vuln.get('port', 'unknown')}\\n\"\n                formatted += f\"  Script: {vuln.get('script', 'unknown')}\\n\"\n                formatted += f\"  Severidade: {vuln.get('severity', 'unknown')}\\n\\n\"\n        \n        return formatted\n    \n    def check_firewall_status(self):\n        \"\"\"Verificar status do firewall\"\"\"\n        try:\n            status = self.firewall_manager.check_firewall_status()\n            \n            formatted = json.dumps(status, indent=2, ensure_ascii=False)\n            self.firewall_status.setText(formatted)\n            \n            self.log_message(\"Firewall\", \"Status verificado\")\n            \n        except Exception as e:\n            self.firewall_status.setText(f\"Erro ao verificar status: {str(e)}\")\n            self.log_message(\"Firewall\", f\"Erro: {str(e)}\", \"error\")\n    \n    def apply_firewall_hardening(self):\n        \"\"\"Aplicar hardening do firewall\"\"\"\n        dry_run = self.dry_run_checkbox.isChecked()\n        \n        if not dry_run:\n            reply = self.show_question(\n                \"Confirmar Hardening\",\n                \"Tem certeza que deseja aplicar hardening real? Isso pode alterar configurações do sistema.\"\n            )\n            if reply != QMessageBox.Yes:\n                return\n        \n        try:\n            result = self.firewall_manager.apply_basic_hardening(dry_run=dry_run)\n            \n            formatted = json.dumps(result, indent=2, ensure_ascii=False)\n            self.firewall_logs.setText(formatted)\n            \n            mode = \"(dry-run)\" if dry_run else \"(REAL)\"\n            self.log_message(\"Firewall\", f\"Hardening aplicado {mode}\")\n            \n        except Exception as e:\n            self.firewall_logs.setText(f\"Erro no hardening: {str(e)}\")\n            self.log_message(\"Firewall\", f\"Erro no hardening: {str(e)}\", \"error\")\n    \n    def backup_firewall(self):\n        \"\"\"Fazer backup do firewall\"\"\"\n        try:\n            backup_file = self.firewall_manager.backup_current_config()\n            self.show_message(\"Backup\", f\"Backup criado: {backup_file}\")\n            self.log_message(\"Firewall\", f\"Backup criado: {backup_file}\")\n            \n        except Exception as e:\n            self.show_message(\"Erro\", f\"Erro ao criar backup: {str(e)}\")\n            self.log_message(\"Firewall\", f\"Erro no backup: {str(e)}\", \"error\")\n    \n    def run_security_assessment(self):\n        \"\"\"Executar avaliação de segurança\"\"\"\n        # Desabilitar botão temporariamente\n        sender = self.sender()\n        if sender:\n            sender.setEnabled(False)\n        \n        # Iniciar thread de hardening\n        self.hardening_thread = HardeningThread()\n        self.hardening_thread.finished.connect(self.on_hardening_finished)\n        self.hardening_thread.progress.connect(self.update_scan_progress)\n        self.hardening_thread.start()\n        \n        self.log_message(\"Hardening\", \"Iniciando avaliação de segurança\")\n    \n    def on_hardening_finished(self, result: Dict[str, Any]):\n        \"\"\"Processar resultado da avaliação\"\"\"\n        # Reabilitar botão\n        for button in self.findChildren(QPushButton):\n            if button.text() == \"Executar Avaliação\":\n                button.setEnabled(True)\n        \n        if \"error\" in result:\n            self.show_message(\"Erro\", f\"Erro na avaliação: {result['error']}\")\n            return\n        \n        # Atualizar score\n        score = result.get('overall_score', 0)\n        self.security_score.setText(f\"Score: {score}/100\")\n        \n        # Cor do score baseado no valor\n        if score >= 80:\n            color = \"#00ff00\"  # Verde\n        elif score >= 60:\n            color = \"#ffff00\"  # Amarelo\n        else:\n            color = \"#ff0000\"  # Vermelho\n        \n        self.security_score.setStyleSheet(f\"color: {color}; font-weight: bold;\")\n        \n        # Atualizar tabela de checks\n        self.update_security_checks_table(result.get('checks', {}))\n        \n        # Atualizar recomendações\n        recommendations = result.get('recommendations', [])\n        self.recommendations_list.setText('\\n'.join(f\"• {rec}\" for rec in recommendations))\n        \n        self.log_message(\"Hardening\", f\"Avaliação concluída - Score: {score}/100\")\n    \n    def update_security_checks_table(self, checks: Dict[str, Any]):\n        \"\"\"Atualizar tabela de checks de segurança\"\"\"\n        self.security_checks.setRowCount(len(checks))\n        \n        row = 0\n        for check_name, check_data in checks.items():\n            # Nome do check\n            self.security_checks.setItem(row, 0, QTableWidgetItem(check_name))\n            \n            # Status\n            status = check_data.get('status', 'unknown') if isinstance(check_data, dict) else 'error'\n            status_item = QTableWidgetItem(status.upper())\n            \n            # Cor baseada no status\n            colors = {\n                'good': QColor(0, 255, 0),\n                'warning': QColor(255, 255, 0),\n                'critical': QColor(255, 0, 0),\n                'error': QColor(255, 100, 100),\n                'info': QColor(0, 212, 255)\n            }\n            \n            if status in colors:\n                status_item.setForeground(colors[status])\n            \n            self.security_checks.setItem(row, 1, status_item)\n            \n            # Detalhes\n            details = \"\"\n            if isinstance(check_data, dict):\n                if 'message' in check_data:\n                    details = check_data['message']\n                elif 'error' in check_data:\n                    details = check_data['error']\n                else:\n                    details = f\"{len(str(check_data))} parâmetros\"\n            \n            self.security_checks.setItem(row, 2, QTableWidgetItem(details))\n            \n            row += 1\n        \n        self.security_checks.resizeColumnsToContents()\n    \n    def create_new_agent(self):\n        \"\"\"Criar novo agente\"\"\"\n        agent_name, ok = QInputDialog.getText(\n            self, \"Novo Agente\", \"Nome do agente:\"\n        )\n        \n        if ok and agent_name:\n            try:\n                credentials = generate_agent_credentials(agent_name)\n                \n                # Mostrar credenciais\n                message = f\"Agente criado com sucesso!\\n\\n\"\n                message += f\"Nome: {agent_name}\\n\"\n                message += f\"Agent ID: {credentials['agent_id']}\\n\"\n                message += f\"Token: {credentials['token'][:20]}...\\n\\n\"\n                message += \"Salve essas credenciais com segurança!\"\n                \n                self.show_message(\"Agente Criado\", message)\n                \n                self.log_message(\"Agentes\", f\"Agente criado: {agent_name}\")\n                self.refresh_agents()\n                \n            except Exception as e:\n                self.show_message(\"Erro\", f\"Erro ao criar agente: {str(e)}\")\n                self.log_message(\"Agentes\", f\"Erro ao criar agente: {str(e)}\", \"error\")\n    \n    def refresh_agents(self):\n        \"\"\"Atualizar lista de agentes\"\"\"\n        # Placeholder - implementar conexão com servidor\n        self.agents_table.setRowCount(1)\n        self.agents_table.setItem(0, 0, QTableWidgetItem(\"agent-001\"))\n        self.agents_table.setItem(0, 1, QTableWidgetItem(\"Agente Local\"))\n        self.agents_table.setItem(0, 2, QTableWidgetItem(\"Offline\"))\n        self.agents_table.setItem(0, 3, QTableWidgetItem(\"Nunca\"))\n        self.agents_table.setItem(0, 4, QTableWidgetItem(\"[Conectar]\"))\n    \n    def log_message(self, category: str, message: str, level: str = \"info\"):\n        \"\"\"Adicionar mensagem aos logs\"\"\"\n        timestamp = datetime.now().strftime(\"%H:%M:%S\")\n        \n        # Ícones para diferentes níveis\n        icons = {\n            \"info\": \"ℹ️\",\n            \"warning\": \"⚠️\",\n            \"error\": \"❌\",\n            \"success\": \"✅\"\n        }\n        \n        icon = icons.get(level, \"📋\")\n        log_entry = f\"[{timestamp}] {icon} [{category}] {message}\\n\"\n        \n        self.logs_display.append(log_entry)\n        \n        # Scroll para o final\n        cursor = self.logs_display.textCursor()\n        cursor.movePosition(cursor.End)\n        self.logs_display.setTextCursor(cursor)\n    \n    def clear_logs(self):\n        \"\"\"Limpar logs\"\"\"\n        self.logs_display.clear()\n        self.log_message(\"Sistema\", \"Logs limpos\")\n    \n    def update_status(self):\n        \"\"\"Atualizar status do sistema\"\"\"\n        # Placeholder para atualizações periódicas\n        current_time = datetime.now().strftime(\"%H:%M:%S\")\n        self.system_status.setText(f\"Sistema: Operacional - {current_time}\")\n    \n    def show_message(self, title: str, message: str):\n        \"\"\"Mostrar mensagem\"\"\"\n        msg = QMessageBox()\n        msg.setWindowTitle(title)\n        msg.setText(message)\n        msg.exec_()\n    \n    def show_question(self, title: str, message: str) -> int:\n        \"\"\"Mostrar pergunta com Sim/Não\"\"\"\n        return QMessageBox.question(\n            self, title, message,\n            QMessageBox.Yes | QMessageBox.No,\n            QMessageBox.No\n        )\n    \n    def closeEvent(self, event):\n        \"\"\"Evento de fechamento\"\"\"\n        self.log_message(\"Sistema\", \"Encerrando JARVIS Cyber Security System\")\n        event.accept()\n\ndef main():\n    \"\"\"Função principal\"\"\"\n    app = QApplication(sys.argv)\n    \n    # Configurar ícone da aplicação\n    app.setApplicationName(\"JARVIS Cyber Security\")\n    app.setApplicationVersion(\"1.0.0\")\n    \n    # Criar e mostrar janela principal\n    window = JarvisMainWindow()\n    window.show()\n    \n    # Log inicial\n    window.log_message(\"Sistema\", \"JARVIS Cyber Security System iniciado\", \"success\")\n    \n    sys.exit(app.exec_())\n\nif __name__ == \"__main__\":\n    main()