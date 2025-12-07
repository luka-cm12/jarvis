#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Command Handler
Manipulador de comandos integrado com recursos avançados
"""

import subprocess
import webbrowser
import sys
import os
from datetime import datetime
from pathlib import Path

# Adicionar diretório pai para importações
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from src.modules.network_scanner import NetworkScanner
    from src.modules.mobile_manager import MobileDeviceManager
    from src.modules.pentest_system import NetworkPenetrationTester
    ADVANCED_MODULES_AVAILABLE = True
except ImportError:
    print("Módulos avançados não disponíveis")
    ADVANCED_MODULES_AVAILABLE = False

class CommandHandler:
    """Manipulador de comandos avançado"""
    
    def __init__(self):
        self.network_scanner = None
        self.mobile_manager = None
        self.pentest_system = None
        
        if ADVANCED_MODULES_AVAILABLE:
            try:
                self.network_scanner = NetworkScanner()
                self.mobile_manager = MobileDeviceManager()
                self.pentest_system = NetworkPenetrationTester()
                print("✅ Módulos avançados carregados")
            except Exception as e:
                print(f"⚠️ Erro ao carregar módulos avançados: {e}")
    
    def handle_command(self, text):
        """Processar comando de texto"""
        if not text:
            return ""
        
        txt = text.lower().strip()
        
        # Comandos de sistema
        if any(word in txt for word in ['sair', 'fechar', 'encerrar', 'tchau']):
            return 'Encerrar'
        
        # Comandos de tempo
        if any(word in txt for word in ['horas', 'horário', 'tempo']):
            now = datetime.now()
            return f'São {now.strftime("%H:%M")} de {now.strftime("%d/%m/%Y")}'
        
        # Comandos de navegação
        if 'youtube' in txt:
            webbrowser.open('https://www.youtube.com')
            return 'Abrindo YouTube'
        
        if 'spotify' in txt or 'música' in txt:
            webbrowser.open('https://open.spotify.com')
            return 'Abrindo Spotify para música'
        
        if 'google' in txt:
            webbrowser.open('https://www.google.com')
            return 'Abrindo Google'
        
        if 'gmail' in txt or 'email' in txt:
            webbrowser.open('https://gmail.com')
            return 'Abrindo Gmail'
        
        # Comandos avançados de rede (se disponível)
        if ADVANCED_MODULES_AVAILABLE and self.network_scanner:
            
            if any(word in txt for word in ['scan', 'escanear', 'rede', 'dispositivos']):
                try:
                    devices = self.network_scanner.scan_network("192.168.1.0/24")
                    count = len(devices)
                    return f'Escaneamento concluído. Encontrei {count} dispositivos na rede.'
                except Exception as e:
                    return f'Erro no escaneamento: {e}'
            
            if any(word in txt for word in ['celular', 'mobile', 'android', 'iphone']):
                try:
                    if self.mobile_manager:
                        devices = self.mobile_manager.discover_mobile_devices("192.168.1.0/24")
                        count = len(devices)
                        return f'Encontrei {count} dispositivos móveis na rede.'
                except Exception as e:
                    return f'Erro na detecção móvel: {e}'
            
            if any(word in txt for word in ['pentest', 'penetração', 'segurança', 'vulnerabilidade']):
                try:
                    if self.pentest_system:
                        return 'Iniciando análise de segurança da rede. Aguarde...'
                except Exception as e:
                    return f'Erro no teste de penetração: {e}'
        
        # Comandos de automação
        if 'calculadora' in txt:
            try:
                subprocess.run(['calc'], check=True)
                return 'Abrindo calculadora'
            except:
                return 'Não foi possível abrir a calculadora'
        
        if 'bloco de notas' in txt or 'notepad' in txt:
            try:
                subprocess.run(['notepad'], check=True)
                return 'Abrindo bloco de notas'
            except:
                return 'Não foi possível abrir o bloco de notas'
        
        # Comandos de status
        if any(word in txt for word in ['status', 'situação', 'como está']):
            status = self.get_system_status()
            return f'Sistema funcionando: {status}'
        
        # Se não encontrou comando específico
        return ''
    
    def get_system_status(self):
        """Obter status do sistema"""
        status_items = []
        
        if ADVANCED_MODULES_AVAILABLE:
            status_items.append("Módulos avançados ativos")
            if self.network_scanner:
                status_items.append("Scanner de rede online")
            if self.mobile_manager:
                status_items.append("Gerenciador móvel online")
            if self.pentest_system:
                status_items.append("Sistema de pentest online")
        else:
            status_items.append("Modo básico")
        
        return ", ".join(status_items) if status_items else "Sistemas básicos ativos"
    
    def execute_network_scan(self, target_range="192.168.1.0/24"):
        """Executar escaneamento de rede"""
        if not self.network_scanner:
            return {"error": "Scanner não disponível"}
        
        try:
            devices = self.network_scanner.scan_network(target_range)
            return {
                "success": True,
                "devices": devices,
                "count": len(devices),
                "range": target_range
            }
        except Exception as e:
            return {"error": str(e)}
    
    def execute_mobile_detection(self, target_range="192.168.1.0/24"):
        """Executar detecção de dispositivos móveis"""
        if not self.mobile_manager:
            return {"error": "Gerenciador móvel não disponível"}
        
        try:
            devices = self.mobile_manager.discover_mobile_devices(target_range)
            profiles = []
            for device in devices:
                profile = self.mobile_manager.create_device_profile(device['device_info'])
                profiles.append(profile)
            
            return {
                "success": True,
                "devices": profiles,
                "count": len(profiles),
                "range": target_range
            }
        except Exception as e:
            return {"error": str(e)}

# Função para compatibilidade
def handle_command(text):
    """Função simples para compatibilidade"""
    handler = CommandHandler()
    return handler.handle_command(text)