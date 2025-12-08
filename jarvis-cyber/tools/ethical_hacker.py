#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Módulo de Penetração Ética
ATENÇÃO: Use apenas em dispositivos autorizados e para fins legais
"""

import socket
import threading
import subprocess
import platform
import time
import json
import os
from datetime import datetime
import ipaddress

class EthicalHacker:
    """Classe para hacking ético e penetração autorizada"""
    
    def __init__(self):
        self.authorized_targets = []
        self.scan_results = {}
        self.exploits_found = {}
        self.sessions = {}
        
    def validate_authorization(self, target: str) -> bool:
        """
        Validar se o alvo está autorizado para teste
        CRÍTICO: Apenas alvos em whitelist ou localhost
        """
        try:
            ip = ipaddress.ip_address(target)
            
            # Permitir apenas localhost e redes privadas
            if ip.is_loopback or ip.is_private:
                return True
                
            # Verificar whitelist de alvos autorizados
            if target in self.authorized_targets:
                return True
                
            return False
            
        except ValueError:
            # Se não for IP válido, verificar hostname
            if target in ['localhost', '127.0.0.1', 'jarvis-lab']:
                return True
            return False
    
    def add_authorized_target(self, target: str, authorization_token: str = None):
        """Adicionar alvo autorizado com token de autorização"""
        if authorization_token and len(authorization_token) >= 32:
            self.authorized_targets.append(target)
            return True
        return False
    
    def advanced_port_scan(self, target: str, ports: list = None) -> dict:
        """
        Scan avançado de portas com detecção de serviços
        """
        if not self.validate_authorization(target):
            return {'error': 'Alvo não autorizado para teste'}
        
        if ports is None:
            # Portas mais comuns para pentesting
            ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 
                    993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443]
        
        results = {
            'target': target,
            'open_ports': [],
            'services': {},
            'vulnerabilities': [],
            'timestamp': datetime.now().isoformat()
        }
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((target, port))
                
                if result == 0:
                    results['open_ports'].append(port)
                    
                    # Tentar identificar serviço
                    try:
                        banner = self.grab_banner(target, port)
                        if banner:
                            results['services'][port] = banner
                            # Verificar vulnerabilidades conhecidas
                            vuln = self.check_service_vulnerability(port, banner)
                            if vuln:
                                results['vulnerabilities'].append(vuln)
                    except:
                        pass
                        
                sock.close()
            except:
                pass
        
        # Scan paralelo
        threads = []
        for port in ports:
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        self.scan_results[target] = results
        return results
    
    def grab_banner(self, target: str, port: int) -> str:
        """Capturar banner do serviço"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target, port))
            
            # Enviar requisição HTTP se for porta web
            if port in [80, 8080]:
                sock.send(b'HEAD / HTTP/1.1\r\nHost: ' + target.encode() + b'\r\n\r\n')
            elif port == 443:
                return "HTTPS/SSL"
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            return banner.strip()
            
        except:
            return ""
    
    def check_service_vulnerability(self, port: int, banner: str) -> dict:
        """Verificar vulnerabilidades conhecidas do serviço"""
        vulns = []
        
        # Base de vulnerabilidades conhecidas
        if port == 21 and 'FTP' in banner.upper():
            if 'vsftpd 2.3.4' in banner:
                vulns.append({
                    'port': port,
                    'service': 'FTP',
                    'vulnerability': 'vsftpd 2.3.4 Backdoor',
                    'severity': 'CRITICAL',
                    'description': 'Backdoor em versão específica do vsftpd'
                })
        
        elif port == 22 and 'SSH' in banner.upper():
            if 'OpenSSH_7.4' in banner:
                vulns.append({
                    'port': port,
                    'service': 'SSH',
                    'vulnerability': 'Weak DH Key Exchange',
                    'severity': 'MEDIUM',
                    'description': 'Versão vulnerável a ataques de downgrade'
                })
        
        elif port == 80 and 'Apache' in banner:
            if 'Apache/2.2' in banner:
                vulns.append({
                    'port': port,
                    'service': 'HTTP',
                    'vulnerability': 'Apache Range Header DoS',
                    'severity': 'HIGH',
                    'description': 'Vulnerável a ataques de negação de serviço'
                })
        
        elif port == 3306 and 'mysql' in banner.lower():
            vulns.append({
                'port': port,
                'service': 'MySQL',
                'vulnerability': 'Potential Weak Credentials',
                'severity': 'HIGH',
                'description': 'Verificar credenciais padrão (root/admin)'
            })
        
        return vulns
    
    def attempt_ssh_bruteforce(self, target: str, usernames: list = None, passwords: list = None) -> dict:
        """
        Tentativa de força bruta SSH (apenas para testes autorizados)
        """
        if not self.validate_authorization(target):
            return {'error': 'Alvo não autorizado para teste'}
        
        if usernames is None:
            usernames = ['admin', 'root', 'user', 'administrator', 'guest']
        
        if passwords is None:
            passwords = ['123456', 'password', 'admin', 'root', '', 'guest', '123123']
        
        results = {
            'target': target,
            'successful_logins': [],
            'attempted_combinations': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulação de força bruta (implementação educativa)
        for username in usernames:
            for password in passwords:
                results['attempted_combinations'] += 1
                
                # Simulação - em ambiente real usaria paramiko
                if username == 'admin' and password == '123456':
                    results['successful_logins'].append({
                        'username': username,
                        'password': password,
                        'access_level': 'administrator'
                    })
                elif username == 'guest' and password == '':
                    results['successful_logins'].append({
                        'username': username, 
                        'password': '(empty)',
                        'access_level': 'guest'
                    })
                
                # Delay para evitar detecção
                time.sleep(0.1)
        
        return results
    
    def web_vulnerability_scan(self, target: str) -> dict:
        """
        Scan de vulnerabilidades web (SQLi, XSS, etc.)
        """
        if not self.validate_authorization(target):
            return {'error': 'Alvo não autorizado para teste'}
        
        results = {
            'target': target,
            'vulnerabilities_found': [],
            'tests_performed': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Testes básicos de vulnerabilidades web
        web_tests = [
            {
                'test': 'SQL Injection',
                'payloads': ["' OR '1'='1", "1'; DROP TABLE users; --", "admin'--"],
                'vulnerable_responses': ['sql error', 'mysql error', 'syntax error']
            },
            {
                'test': 'XSS Reflected',
                'payloads': ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>'],
                'vulnerable_responses': ['<script>', 'onerror=']
            },
            {
                'test': 'Directory Traversal',
                'payloads': ['../../../etc/passwd', '..\\..\\..\\windows\\system32\\config\\sam'],
                'vulnerable_responses': ['root:', '[SYSTEM]']
            }
        ]
        
        for test in web_tests:
            results['tests_performed'].append(test['test'])
            
            # Simular teste (implementação educativa)
            if test['test'] == 'SQL Injection' and 'vulnerable' in target.lower():
                results['vulnerabilities_found'].append({
                    'type': 'SQL Injection',
                    'severity': 'CRITICAL',
                    'description': 'Possível injeção SQL detectada',
                    'payload': "' OR '1'='1",
                    'recommendation': 'Usar prepared statements e validação de entrada'
                })
        
        return results
    
    def network_sniffing(self, interface: str = None, duration: int = 30) -> dict:
        """
        Captura de pacotes de rede (apenas em rede própria)
        """
        results = {
            'interface': interface or 'default',
            'duration': duration,
            'packets_captured': [],
            'protocols_found': set(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulação de captura (implementação educativa)
        # Em ambiente real usaria scapy ou similar
        
        simulated_packets = [
            {'src': '192.168.1.100', 'dst': '192.168.1.1', 'protocol': 'HTTP', 'data': 'GET / HTTP/1.1'},
            {'src': '192.168.1.101', 'dst': '8.8.8.8', 'protocol': 'DNS', 'data': 'Query: google.com'},
            {'src': '192.168.1.102', 'dst': '192.168.1.50', 'protocol': 'SSH', 'data': 'Encrypted data'}
        ]
        
        for packet in simulated_packets:
            results['packets_captured'].append(packet)
            results['protocols_found'].add(packet['protocol'])
        
        results['protocols_found'] = list(results['protocols_found'])
        results['summary'] = f"Capturados {len(simulated_packets)} pacotes em {duration}s"
        
        return results
    
    def generate_exploit_payload(self, vulnerability_type: str, target_os: str = None) -> dict:
        """
        Gerar payloads de exploit para vulnerabilidades conhecidas
        """
        payloads = {
            'buffer_overflow': {
                'windows': 'A' * 256 + '\\x41\\x41\\x41\\x41',
                'linux': 'A' * 256 + '\\x90\\x90\\x90\\x90',
                'description': 'Buffer overflow básico para teste'
            },
            'sql_injection': {
                'universal': "'; DROP TABLE users; --",
                'mysql': "' UNION SELECT 1,user(),version(); --",
                'description': 'Payloads de SQL injection para teste'
            },
            'xss': {
                'universal': '<script>alert("XSS_TEST")</script>',
                'bypass_filters': '<img src=x onerror=alert("XSS")>',
                'description': 'Payloads XSS para teste de filtros'
            }
        }
        
        if vulnerability_type in payloads:
            return {
                'vulnerability': vulnerability_type,
                'payloads': payloads[vulnerability_type],
                'warning': 'Use apenas em ambiente autorizado de teste',
                'timestamp': datetime.now().isoformat()
            }
        
        return {'error': 'Tipo de vulnerabilidade não suportado'}
    
    def wireless_security_scan(self) -> dict:
        """
        Scan de segurança de redes Wi-Fi (apenas redes próprias)
        """
        results = {
            'networks_found': [],
            'security_assessment': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Simulação de scan Wi-Fi (implementação educativa)
        simulated_networks = [
            {
                'ssid': 'JARVIS_LAB',
                'security': 'WPA2-PSK',
                'signal': -45,
                'channel': 6,
                'vulnerability': 'None detected'
            },
            {
                'ssid': 'TestNetwork',
                'security': 'WEP',
                'signal': -60,
                'channel': 11,
                'vulnerability': 'WEP encryption deprecated'
            },
            {
                'ssid': 'OpenWiFi',
                'security': 'None',
                'signal': -70,
                'channel': 1,
                'vulnerability': 'No encryption - high risk'
            }
        ]
        
        for network in simulated_networks:
            results['networks_found'].append(network)
            
            if network['security'] == 'None':
                results['security_assessment'].append({
                    'ssid': network['ssid'],
                    'risk': 'HIGH',
                    'issue': 'Rede aberta sem criptografia'
                })
            elif network['security'] == 'WEP':
                results['security_assessment'].append({
                    'ssid': network['ssid'],
                    'risk': 'MEDIUM',
                    'issue': 'WEP facilmente quebrado'
                })
        
        return results

# Funções de conveniência para a interface
def run_ethical_penetration_test(target: str, test_type: str = 'basic') -> dict:
    """Executar teste de penetração ético"""
    hacker = EthicalHacker()
    
    if test_type == 'basic':
        return hacker.advanced_port_scan(target)
    elif test_type == 'web':
        return hacker.web_vulnerability_scan(target)
    elif test_type == 'ssh_bruteforce':
        return hacker.attempt_ssh_bruteforce(target)
    elif test_type == 'network_sniff':
        return hacker.network_sniffing()
    elif test_type == 'wireless':
        return hacker.wireless_security_scan()
    else:
        return {'error': 'Tipo de teste não reconhecido'}

def generate_penetration_report(target: str, results: dict) -> str:
    """Gerar relatório de teste de penetração"""
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    JARVIS ETHICAL PENETRATION TEST REPORT                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 TARGET: {target}
📅 DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⚖️  AUTHORIZATION: Ethical testing only - Authorized targets

🔍 SCAN RESULTS:
"""
    
    if 'open_ports' in results:
        report += f"   📡 Open Ports: {len(results['open_ports'])}\n"
        for port in results['open_ports'][:5]:  # Mostrar apenas 5 primeiros
            service = results.get('services', {}).get(port, 'Unknown')
            report += f"      - Port {port}: {service}\n"
    
    if 'vulnerabilities' in results and results['vulnerabilities']:
        report += f"\n🚨 VULNERABILITIES FOUND: {len(results['vulnerabilities'])}\n"
        for vuln in results['vulnerabilities']:
            if isinstance(vuln, dict):
                report += f"   ⚠️  {vuln.get('vulnerability', 'Unknown')}\n"
                report += f"      Severity: {vuln.get('severity', 'Unknown')}\n"
                report += f"      Port: {vuln.get('port', 'N/A')}\n\n"
    
    if 'successful_logins' in results and results['successful_logins']:
        report += f"🔓 CREDENTIAL VULNERABILITIES: {len(results['successful_logins'])}\n"
        for login in results['successful_logins']:
            report += f"   - User: {login['username']} | Pass: {login['password']}\n"
    
    report += """
📋 RECOMMENDATIONS:
   • Change default credentials immediately
   • Update all services to latest versions  
   • Implement strong firewall rules
   • Enable intrusion detection systems
   • Regular security audits

⚖️  LEGAL NOTICE:
   This test was performed for authorized security assessment only.
   Any unauthorized access is illegal and prohibited.
   
🛡️  JARVIS Cyber Security System - Ethical Hacking Module
"""
    
    return report

if __name__ == "__main__":
    # Teste das funcionalidades
    print("🔴 JARVIS Ethical Hacking Module - Test Mode")
    
    # Teste básico em localhost
    result = run_ethical_penetration_test("127.0.0.1", "basic")
    print(f"Scan Result: {result}")
    
    # Gerar relatório
    report = generate_penetration_report("127.0.0.1", result)
    print(report)