#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Advanced Network Scanner
Sistema avançado de descoberta e análise de rede
"""

import socket
import threading
import subprocess
import json
import time
from datetime import datetime
import nmap
import psutil
import requests
from concurrent.futures import ThreadPoolExecutor
import sqlite3

class NetworkScanner:
    """Scanner avançado de rede com capacidades de penetração"""
    
    def __init__(self):
        self.devices = {}
        self.services = {}
        self.vulnerabilities = []
        self.db_path = "data/network_db.sqlite"
        self.init_database()
    
    def init_database(self):
        """Inicializar banco de dados"""
        import os
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de dispositivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                ip TEXT PRIMARY KEY,
                hostname TEXT,
                mac_address TEXT,
                os_type TEXT,
                status TEXT,
                last_seen TIMESTAMP,
                ports TEXT,
                services TEXT
            )
        ''')
        
        # Tabela de vulnerabilidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_ip TEXT,
                vuln_type TEXT,
                severity TEXT,
                description TEXT,
                discovered_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_network_range(self):
        """Obter faixa de rede local"""
        try:
            # Obter IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Calcular rede (assumindo /24)
            network_parts = local_ip.split('.')
            network_base = f"{network_parts[0]}.{network_parts[1]}.{network_parts[2]}"
            
            return f"{network_base}.0/24"
        except Exception as e:
            print(f"Erro ao obter rede: {e}")
            return "192.168.1.0/24"
    
    def ping_sweep(self, network):
        """Varredura de ping na rede"""
        print(f"🔍 Iniciando varredura de rede: {network}")
        active_hosts = []
        
        network_base = network.split('/')[0].rsplit('.', 1)[0]
        
        def ping_host(ip):
            try:
                # Ping no Windows
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', ip],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return ip
            except:
                pass
            return None
        
        # Usar ThreadPoolExecutor para pings paralelos
        with ThreadPoolExecutor(max_workers=50) as executor:
            ips = [f"{network_base}.{i}" for i in range(1, 255)]
            results = list(executor.map(ping_host, ips))
            active_hosts = [ip for ip in results if ip is not None]
        
        print(f"✅ Encontrados {len(active_hosts)} hosts ativos")
        return active_hosts
    
    def port_scan(self, target_ip, ports=None):
        """Scanner de portas avançado"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 1433, 3306, 3389, 5432, 8080]
        
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                sock.close()
                if result == 0:
                    return port
            except:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = list(executor.map(scan_port, ports))
            open_ports = [port for port in results if port is not None]
        
        return open_ports
    
    def service_detection(self, target_ip, ports):
        """Detecção de serviços em portas abertas"""
        services = {}
        
        service_map = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-Alt"
        }
        
        for port in ports:
            try:
                service_name = service_map.get(port, "Unknown")
                
                # Tentar banner grabbing
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((target_ip, port))
                
                # Enviar requisição HTTP básica para portas web
                if port in [80, 8080, 443]:
                    sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                sock.close()
                
                services[port] = {
                    'service': service_name,
                    'banner': banner.strip()
                }
            except:
                services[port] = {
                    'service': service_map.get(port, "Unknown"),
                    'banner': ""
                }
        
        return services
    
    def vulnerability_scan(self, target_ip, services):
        """Scanner básico de vulnerabilidades"""
        vulns = []
        
        for port, service_info in services.items():
            service = service_info['service']
            banner = service_info['banner']
            
            # Verificações básicas de segurança
            if service == "FTP" and "vsFTPd 2.3.4" in banner:
                vulns.append({
                    'type': 'Backdoor',
                    'severity': 'CRITICAL',
                    'description': 'vsFTPd 2.3.4 Backdoor Vulnerability'
                })
            
            if service == "SSH" and "OpenSSH" in banner:
                if "OpenSSH_7.4" in banner:
                    vulns.append({
                        'type': 'CVE',
                        'severity': 'MEDIUM',
                        'description': 'OpenSSH User Enumeration (CVE-2018-15473)'
                    })
            
            if service == "HTTP" and "Server:" in banner:
                if "Apache/2.2" in banner:
                    vulns.append({
                        'type': 'Outdated Software',
                        'severity': 'HIGH',
                        'description': 'Outdated Apache version - multiple vulnerabilities'
                    })
            
            # Verificar portas comuns abertas
            if port == 23:  # Telnet
                vulns.append({
                    'type': 'Insecure Protocol',
                    'severity': 'HIGH',
                    'description': 'Telnet service detected - plaintext authentication'
                })
            
            if port == 21:  # FTP
                vulns.append({
                    'type': 'Insecure Protocol',
                    'severity': 'MEDIUM',
                    'description': 'FTP service detected - consider SFTP/FTPS'
                })
        
        return vulns
    
    def full_network_scan(self):
        """Varredura completa da rede"""
        print("🚀 Iniciando varredura completa da rede...")
        
        network = self.get_network_range()
        active_hosts = self.ping_sweep(network)
        
        all_results = {}
        
        for host in active_hosts:
            print(f"🔎 Analisando host: {host}")
            
            # Scanner de portas
            open_ports = self.port_scan(host)
            
            if open_ports:
                print(f"  📡 Portas abertas: {open_ports}")
                
                # Detecção de serviços
                services = self.service_detection(host, open_ports)
                
                # Scanner de vulnerabilidades
                vulns = self.vulnerability_scan(host, services)
                
                all_results[host] = {
                    'ports': open_ports,
                    'services': services,
                    'vulnerabilities': vulns,
                    'last_scan': datetime.now().isoformat()
                }
                
                # Salvar no banco
                self.save_to_database(host, all_results[host])
        
        return all_results
    
    def save_to_database(self, ip, data):
        """Salvar dados no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (ip, status, last_seen, ports, services)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            ip,
            'active',
            datetime.now().isoformat(),
            json.dumps(data['ports']),
            json.dumps(data['services'])
        ))
        
        # Salvar vulnerabilidades
        for vuln in data['vulnerabilities']:
            cursor.execute('''
                INSERT INTO vulnerabilities
                (target_ip, vuln_type, severity, description, discovered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                ip,
                vuln['type'],
                vuln['severity'],
                vuln['description'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_network_report(self):
        """Gerar relatório da rede"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Dispositivos ativos
        cursor.execute('SELECT * FROM devices')
        devices = cursor.fetchall()
        
        # Vulnerabilidades
        cursor.execute('SELECT * FROM vulnerabilities ORDER BY severity DESC')
        vulns = cursor.fetchall()
        
        conn.close()
        
        return {
            'devices': devices,
            'vulnerabilities': vulns,
            'summary': {
                'total_devices': len(devices),
                'total_vulns': len(vulns),
                'critical_vulns': len([v for v in vulns if v[3] == 'CRITICAL']),
                'high_vulns': len([v for v in vulns if v[3] == 'HIGH'])
            }
        }

# Classe para monitoramento contínuo
class NetworkMonitor:
    """Monitor contínuo da rede"""
    
    def __init__(self):
        self.scanner = NetworkScanner()
        self.running = False
        self.scan_interval = 300  # 5 minutos
    
    def start_monitoring(self):
        """Iniciar monitoramento contínuo"""
        self.running = True
        
        def monitor_loop():
            while self.running:
                try:
                    print("🔄 Executando varredura de monitoramento...")
                    self.scanner.full_network_scan()
                    time.sleep(self.scan_interval)
                except Exception as e:
                    print(f"❌ Erro no monitoramento: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.running = False

if __name__ == "__main__":
    # Teste do scanner
    scanner = NetworkScanner()
    results = scanner.full_network_scan()
    
    print("\n📊 RELATÓRIO DE REDE:")
    print("=" * 50)
    
    for ip, data in results.items():
        print(f"\n🖥️  HOST: {ip}")
        print(f"   📡 Portas: {data['ports']}")
        
        if data['vulnerabilities']:
            print("   ⚠️  VULNERABILIDADES:")
            for vuln in data['vulnerabilities']:
                print(f"      🔴 {vuln['severity']}: {vuln['description']}")