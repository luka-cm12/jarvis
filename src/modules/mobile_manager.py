#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Mobile Device Manager
Sistema avançado para detecção e análise de dispositivos móveis na rede
"""

import socket
import threading
import subprocess
import json
import time
from datetime import datetime
import requests
import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor
import struct

class MobileDeviceManager:
    """Gerenciador de dispositivos móveis"""
    
    def __init__(self):
        self.mobile_devices = {}
        self.device_fingerprints = {}
        self.db_path = "data/mobile_devices.sqlite"
        self.init_database()
    
    def init_database(self):
        """Inicializar banco de dados de dispositivos móveis"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobile_devices (
                device_id TEXT PRIMARY KEY,
                ip_address TEXT,
                mac_address TEXT,
                device_type TEXT,
                os_version TEXT,
                manufacturer TEXT,
                model TEXT,
                last_seen TIMESTAMP,
                capabilities TEXT,
                security_analysis TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                interaction_type TEXT,
                data TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def discover_mobile_devices(self, network_range):
        """Descobrir dispositivos móveis na rede"""
        print(f"🔍 Procurando dispositivos móveis em {network_range}")
        
        mobile_devices = []
        network_base = network_range.split('/')[0].rsplit('.', 1)[0]
        
        def analyze_device(ip):
            try:
                # Verificar se é um dispositivo móvel
                device_info = self.analyze_device_fingerprint(ip)
                if device_info and device_info.get('is_mobile'):
                    return {
                        'ip': ip,
                        'device_info': device_info
                    }
            except Exception as e:
                print(f"Erro ao analisar {ip}: {e}")
            return None
        
        # Escanear IPs em paralelo
        with ThreadPoolExecutor(max_workers=50) as executor:
            ips = [f"{network_base}.{i}" for i in range(1, 255)]
            results = list(executor.map(analyze_device, ips))
            mobile_devices = [result for result in results if result is not None]
        
        print(f"📱 Encontrados {len(mobile_devices)} dispositivos móveis")
        return mobile_devices
    
    def analyze_device_fingerprint(self, ip):
        """Analisar fingerprint do dispositivo"""
        device_info = {
            'ip': ip,
            'is_mobile': False,
            'os_type': 'unknown',
            'manufacturer': 'unknown',
            'capabilities': []
        }
        
        try:
            # Análise de portas para detectar serviços móveis
            mobile_ports = [5353, 62078, 7000, 7001, 7070, 8080, 8443]
            open_ports = []
            
            for port in mobile_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            
            # Verificar se há serviços típicos de dispositivos móveis
            if open_ports:
                device_info['open_ports'] = open_ports
                
                # Detecção específica de iOS
                if 62078 in open_ports or 7000 in open_ports:
                    device_info['is_mobile'] = True
                    device_info['os_type'] = 'iOS'
                    device_info['manufacturer'] = 'Apple'
                    device_info['capabilities'].extend(['AirPlay', 'AirDrop'])
                
                # Detecção específica de Android
                if 5353 in open_ports:  # mDNS comum em Android
                    device_info['is_mobile'] = True
                    if device_info['os_type'] == 'unknown':
                        device_info['os_type'] = 'Android'
                        device_info['capabilities'].append('mDNS')
            
            # Análise adicional via HTTP
            if 8080 in open_ports or 8443 in open_ports:
                device_info.update(self.analyze_http_service(ip))
            
            # Análise de TTL para detectar SO
            ttl_info = self.analyze_ttl(ip)
            if ttl_info:
                device_info.update(ttl_info)
            
        except Exception as e:
            print(f"Erro na análise de fingerprint para {ip}: {e}")
        
        return device_info
    
    def analyze_http_service(self, ip):
        """Analisar serviços HTTP para identificar dispositivo"""
        info = {}
        
        try:
            # Tentar conectar em portas HTTP comuns
            for port in [8080, 8443, 80, 443]:
                try:
                    url = f"http://{ip}:{port}"
                    response = requests.get(url, timeout=3, headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; NetworkScanner/1.0)'
                    })
                    
                    # Analisar headers para detectar dispositivo
                    server_header = response.headers.get('Server', '')
                    
                    if 'iPhone' in server_header or 'iOS' in server_header:
                        info['is_mobile'] = True
                        info['os_type'] = 'iOS'
                        info['manufacturer'] = 'Apple'
                    elif 'Android' in server_header:
                        info['is_mobile'] = True
                        info['os_type'] = 'Android'
                    
                    # Verificar se há interface web de dispositivo móvel
                    if 'mobile' in response.text.lower():
                        info['has_web_interface'] = True
                        info['web_port'] = port
                    
                    break
                    
                except requests.exceptions.RequestException:
                    continue
                    
        except Exception as e:
            pass
        
        return info
    
    def analyze_ttl(self, ip):
        """Analisar TTL para detectar sistema operacional"""
        try:
            # Fazer ping e analisar TTL
            result = subprocess.run(
                ['ping', '-n', '1', ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Extrair TTL do output do ping
                for line in output.split('\n'):
                    if 'TTL=' in line:
                        ttl = int(line.split('TTL=')[1].split()[0])
                        
                        # TTL típicos por OS
                        if ttl <= 64:
                            if ttl == 64:
                                return {'os_hint': 'Linux/Android', 'ttl': ttl}
                            else:
                                return {'os_hint': 'iOS/macOS', 'ttl': ttl}
                        elif ttl <= 128:
                            return {'os_hint': 'Windows', 'ttl': ttl}
                        
        except Exception:
            pass
        
        return {}
    
    def create_device_profile(self, device_data):
        """Criar perfil detalhado do dispositivo"""
        profile = {
            'device_id': f"{device_data['ip']}_{int(time.time())}",
            'basic_info': device_data,
            'capabilities': self.enumerate_capabilities(device_data),
            'security_assessment': self.assess_security(device_data),
            'interaction_methods': self.get_interaction_methods(device_data)
        }
        
        self.save_device_profile(profile)
        return profile
    
    def enumerate_capabilities(self, device_data):
        """Enumerar capacidades do dispositivo"""
        capabilities = []
        
        # Verificar capacidades baseadas no OS
        if device_data.get('os_type') == 'iOS':
            capabilities.extend([
                'AirPlay_receiver',
                'AirDrop_capable',
                'Siri_integration',
                'HomeKit_compatible',
                'iCloud_sync'
            ])
        elif device_data.get('os_type') == 'Android':
            capabilities.extend([
                'Google_Cast_receiver',
                'NFC_capable',
                'Bluetooth_LE',
                'WiFi_Direct',
                'Android_Auto'
            ])
        
        # Verificar capacidades baseadas em portas abertas
        open_ports = device_data.get('open_ports', [])
        
        if 5353 in open_ports:
            capabilities.append('mDNS_discovery')
        if 8080 in open_ports:
            capabilities.append('HTTP_interface')
        if 62078 in open_ports:
            capabilities.append('AirPlay_streaming')
        
        return capabilities
    
    def assess_security(self, device_data):
        """Avaliar segurança do dispositivo"""
        security_issues = []
        recommendations = []
        
        # Verificar portas abertas desnecessárias
        open_ports = device_data.get('open_ports', [])
        
        if 23 in open_ports:  # Telnet
            security_issues.append("Telnet ativo - protocolo inseguro")
            recommendations.append("Desativar Telnet e usar SSH")
        
        if 8080 in open_ports:
            security_issues.append("Interface HTTP sem autenticação detectada")
            recommendations.append("Implementar autenticação na interface web")
        
        # Análise baseada no OS
        os_type = device_data.get('os_type')
        if os_type == 'Android':
            security_issues.append("Verificar se Developer Options estão desabilitadas")
            recommendations.append("Manter Android sempre atualizado")
        elif os_type == 'iOS':
            recommendations.append("Verificar se iOS está na versão mais recente")
        
        return {
            'security_level': 'MEDIUM' if security_issues else 'HIGH',
            'issues': security_issues,
            'recommendations': recommendations
        }
    
    def get_interaction_methods(self, device_data):
        """Obter métodos de interação disponíveis"""
        methods = []
        
        os_type = device_data.get('os_type')
        open_ports = device_data.get('open_ports', [])
        
        # Métodos baseados no OS
        if os_type == 'iOS':
            methods.extend([
                {'type': 'AirPlay', 'port': 7000, 'description': 'Streaming de mídia'},
                {'type': 'AirDrop', 'port': 'dynamic', 'description': 'Transferência de arquivos'}
            ])
        elif os_type == 'Android':
            methods.extend([
                {'type': 'ADB', 'port': 5555, 'description': 'Android Debug Bridge'},
                {'type': 'HTTP', 'port': 8080, 'description': 'Interface web'}
            ])
        
        # Métodos baseados em portas abertas
        if 8080 in open_ports:
            methods.append({
                'type': 'WebInterface', 
                'port': 8080, 
                'description': 'Interface web administrativa'
            })
        
        return methods
    
    def save_device_profile(self, profile):
        """Salvar perfil do dispositivo no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO mobile_devices 
            (device_id, ip_address, device_type, os_version, manufacturer, 
             last_seen, capabilities, security_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile['device_id'],
            profile['basic_info']['ip'],
            profile['basic_info'].get('os_type', 'unknown'),
            'unknown',  # version detection would need more analysis
            profile['basic_info'].get('manufacturer', 'unknown'),
            datetime.now().isoformat(),
            json.dumps(profile['capabilities']),
            json.dumps(profile['security_assessment'])
        ))
        
        conn.commit()
        conn.close()
    
    def generate_mobile_interface(self):
        """Gerar interface móvel responsiva"""
        mobile_html = self.create_mobile_html()
        mobile_css = self.create_mobile_css()
        mobile_js = self.create_mobile_js()
        
        return {
            'html': mobile_html,
            'css': mobile_css,
            'js': mobile_js
        }
    
    def create_mobile_html(self):
        """Criar HTML otimizado para mobile"""
        return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>JARVIS Mobile</title>
    <link rel="apple-touch-icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0e27, #16213e);
            color: #00d4ff;
            height: 100vh;
            overflow-x: hidden;
            -webkit-user-select: none;
        }
        
        .mobile-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(0, 212, 255, 0.1);
            backdrop-filter: blur(20px);
        }
        
        .logo {
            font-size: 24px;
            font-weight: bold;
            text-shadow: 0 0 10px currentColor;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #00ff88;
            box-shadow: 0 0 10px currentColor;
        }
        
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        
        .command-section {
            margin-bottom: 30px;
        }
        
        .voice-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .text-input {
            flex: 1;
            padding: 15px;
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 25px;
            background: rgba(0, 212, 255, 0.05);
            color: #00d4ff;
            font-size: 16px;
        }
        
        .voice-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #00d4ff, #0066cc);
            color: white;
            font-size: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .voice-btn:active {
            transform: scale(0.95);
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .action-card {
            padding: 20px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 15px;
            border: 1px solid rgba(0, 212, 255, 0.2);
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .action-card:active {
            transform: scale(0.95);
            background: rgba(0, 212, 255, 0.2);
        }
        
        .device-list {
            max-height: 40vh;
            overflow-y: auto;
        }
        
        .device-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin-bottom: 10px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border-left: 3px solid #00ff88;
        }
        
        .bottom-nav {
            display: flex;
            justify-content: space-around;
            padding: 15px 0;
            background: rgba(0, 212, 255, 0.1);
            backdrop-filter: blur(20px);
        }
        
        .nav-item {
            padding: 10px 20px;
            text-align: center;
            cursor: pointer;
            border-radius: 15px;
            transition: all 0.3s ease;
        }
        
        .nav-item.active {
            background: rgba(0, 212, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="mobile-container">
        <div class="header">
            <div class="logo">JARVIS</div>
            <div class="status-indicator" id="statusIndicator"></div>
        </div>
        
        <div class="main-content" id="mainContent">
            <!-- Conteúdo dinâmico será carregado aqui -->
        </div>
        
        <div class="bottom-nav">
            <div class="nav-item active" onclick="showSection('home')">🏠</div>
            <div class="nav-item" onclick="showSection('devices')">📱</div>
            <div class="nav-item" onclick="showSection('network')">🌐</div>
            <div class="nav-item" onclick="showSection('settings')">⚙️</div>
        </div>
    </div>
    
    <script>
        // JavaScript será adicionado aqui
    </script>
</body>
</html>
        '''
    
    def get_full_report(self):
        """Gerar relatório completo de dispositivos móveis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM mobile_devices')
        devices = cursor.fetchall()
        
        conn.close()
        
        report = {
            'total_devices': len(devices),
            'devices_by_os': {},
            'security_summary': {
                'high_security': 0,
                'medium_security': 0,
                'low_security': 0
            },
            'devices': []
        }
        
        for device in devices:
            device_dict = {
                'device_id': device[0],
                'ip_address': device[1],
                'device_type': device[3],
                'manufacturer': device[5],
                'capabilities': json.loads(device[7]) if device[7] else [],
                'security_analysis': json.loads(device[8]) if device[8] else {}
            }
            
            report['devices'].append(device_dict)
            
            # Contar por OS
            os_type = device_dict['device_type']
            report['devices_by_os'][os_type] = report['devices_by_os'].get(os_type, 0) + 1
            
            # Contar por segurança
            security_level = device_dict['security_analysis'].get('security_level', 'MEDIUM')
            if security_level == 'HIGH':
                report['security_summary']['high_security'] += 1
            elif security_level == 'LOW':
                report['security_summary']['low_security'] += 1
            else:
                report['security_summary']['medium_security'] += 1
        
        return report

if __name__ == "__main__":
    # Teste do sistema
    manager = MobileDeviceManager()
    
    print("📱 JARVIS Mobile Device Manager")
    print("=" * 40)
    
    # Descobrir dispositivos móveis
    devices = manager.discover_mobile_devices("192.168.1.0/24")
    
    for device in devices:
        print(f"\n📱 Dispositivo encontrado: {device['ip']}")
        profile = manager.create_device_profile(device['device_info'])
        print(f"   OS: {profile['basic_info'].get('os_type', 'Unknown')}")
        print(f"   Fabricante: {profile['basic_info'].get('manufacturer', 'Unknown')}")
        print(f"   Capacidades: {len(profile['capabilities'])}")
        print(f"   Nível de segurança: {profile['security_assessment']['security_level']}")
    
    # Gerar relatório
    report = manager.get_full_report()
    print(f"\n📊 RELATÓRIO FINAL:")
    print(f"   Total de dispositivos: {report['total_devices']}")
    print(f"   Por OS: {report['devices_by_os']}")
    print(f"   Segurança: {report['security_summary']}")