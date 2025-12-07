#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Network Scanner
Scanner de rede defensivo com controles de segurança
"""

import nmap
import logging
import time
import ipaddress
import socket
import subprocess
from typing import Dict, List, Optional, Any
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jarvis.scanner')

# Configurações de segurança
MAX_SCAN_RANGE = 1024  # Máximo de IPs em um scan
TIMEOUT_PER_HOST = 30  # Timeout por host
MAX_PORTS_QUICK = 1000  # Máximo de portas para scan rápido
MAX_PORTS_FULL = 65535  # Máximo de portas para scan completo

# Portas comuns para scan rápido
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
    1723, 3306, 3389, 5432, 5900, 8080, 8443, 8888, 9090
]

class SecureScanner:
    """
    Scanner de rede defensivo com controles de segurança
    """
    
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.scan_history = []
    
    def validate_target(self, target: str) -> tuple[bool, str]:
        """
        Validar alvo do scan
        
        Args:
            target: IP, CIDR ou hostname
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Verificar se é uma rede CIDR
            if '/' in target:
                network = ipaddress.ip_network(target, strict=False)
                
                # Verificar tamanho da rede
                if network.num_addresses > MAX_SCAN_RANGE:
                    return False, f"Rede muito grande: {network.num_addresses} IPs (máx: {MAX_SCAN_RANGE})"
                
                # Verificar se não é rede pública
                if network.is_global:
                    return False, "Scans de redes públicas não são permitidos"
                
                return True, ""
            
            # Verificar IP único
            else:
                try:
                    ip = ipaddress.ip_address(target)
                    if ip.is_global:
                        return False, "Scans de IPs públicos não são permitidos"
                except ipaddress.AddressValueError:
                    # Pode ser hostname - verificar se resolve para IP privado
                    try:
                        resolved_ip = socket.gethostbyname(target)
                        ip = ipaddress.ip_address(resolved_ip)
                        if ip.is_global:
                            return False, "Hostname resolve para IP público"
                    except socket.gaierror:
                        return False, f"Não foi possível resolver hostname: {target}"
                
                return True, ""
                
        except Exception as e:
            return False, f"Erro na validação do alvo: {str(e)}"
    
    def scan_host_basic(self, target: str) -> Dict[str, Any]:
        """
        Scan básico de host (ping + OS detection)
        
        Args:
            target: IP ou hostname
        
        Returns:
            Resultado do scan
        """
        logger.info(f"Iniciando scan básico em {target}")
        
        try:
            # Scan básico com detecção de OS
            scan_args = '-sn -O --osscan-guess --max-retries 1'
            result = self.nm.scan(target, arguments=scan_args)
            
            scan_result = {
                'target': target,
                'scan_type': 'basic',
                'timestamp': time.time(),
                'hosts_scanned': len(result['scan']),
                'hosts_up': 0,
                'hosts': []
            }
            
            for host, data in result['scan'].items():
                if data['status']['state'] == 'up':
                    scan_result['hosts_up'] += 1
                    
                    host_info = {
                        'ip': host,
                        'hostname': data.get('hostnames', [{}])[0].get('name', ''),
                        'state': data['status']['state'],
                        'os': self._extract_os_info(data)
                    }
                    
                    scan_result['hosts'].append(host_info)
            
            self._log_scan(scan_result)
            return scan_result
            
        except Exception as e:
            logger.error(f"Erro no scan básico: {e}")
            return {
                'target': target,
                'scan_type': 'basic',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def scan_ports_quick(self, target: str) -> Dict[str, Any]:
        """
        Scan rápido de portas comuns
        
        Args:
            target: IP ou hostname
        
        Returns:
            Resultado do scan
        """
        logger.info(f"Iniciando scan rápido de portas em {target}")
        
        try:
            # Converter lista de portas para string
            ports_str = ','.join(map(str, COMMON_PORTS))
            
            # Scan TCP das portas comuns
            scan_args = f'-sS -T4 --max-retries 1 --host-timeout {TIMEOUT_PER_HOST}s'
            result = self.nm.scan(target, ports_str, arguments=scan_args)
            
            scan_result = {
                'target': target,
                'scan_type': 'quick_ports',
                'timestamp': time.time(),
                'ports_scanned': len(COMMON_PORTS),
                'hosts': []
            }
            
            for host, data in result['scan'].items():
                if 'tcp' in data:
                    host_ports = []
                    
                    for port, port_data in data['tcp'].items():
                        if port_data['state'] == 'open':
                            port_info = {
                                'port': port,
                                'state': port_data['state'],
                                'service': port_data.get('name', 'unknown'),
                                'product': port_data.get('product', ''),
                                'version': port_data.get('version', '')
                            }
                            host_ports.append(port_info)
                    
                    if host_ports:
                        host_info = {
                            'ip': host,
                            'hostname': data.get('hostnames', [{}])[0].get('name', ''),
                            'open_ports': host_ports,
                            'ports_open': len(host_ports)
                        }
                        scan_result['hosts'].append(host_info)
            
            self._log_scan(scan_result)
            return scan_result
            
        except Exception as e:
            logger.error(f"Erro no scan rápido: {e}")
            return {
                'target': target,
                'scan_type': 'quick_ports',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def scan_ports_full(self, target: str, port_range: str = '1-1000') -> Dict[str, Any]:
        """
        Scan completo de portas
        
        Args:
            target: IP ou hostname
            port_range: Range de portas (ex: '1-1000')
        
        Returns:
            Resultado do scan
        """
        logger.info(f"Iniciando scan completo em {target}, portas {port_range}")
        
        try:
            # Validar range de portas
            start_port, end_port = map(int, port_range.split('-'))
            if end_port - start_port > MAX_PORTS_FULL:
                raise ValueError(f"Range de portas muito grande: {end_port - start_port}")
            
            # Scan TCP completo com detecção de versão
            scan_args = f'-sS -sV -T4 --version-intensity 5 --max-retries 2 --host-timeout {TIMEOUT_PER_HOST * 2}s'
            result = self.nm.scan(target, port_range, arguments=scan_args)
            
            scan_result = {
                'target': target,
                'scan_type': 'full_ports',
                'port_range': port_range,
                'timestamp': time.time(),
                'hosts': []
            }
            
            for host, data in result['scan'].items():
                host_info = {
                    'ip': host,
                    'hostname': data.get('hostnames', [{}])[0].get('name', ''),
                    'os': self._extract_os_info(data),
                    'open_ports': [],
                    'filtered_ports': [],
                    'closed_ports': 0
                }
                
                if 'tcp' in data:
                    for port, port_data in data['tcp'].items():
                        port_info = {
                            'port': port,
                            'state': port_data['state'],
                            'service': port_data.get('name', 'unknown'),
                            'product': port_data.get('product', ''),
                            'version': port_data.get('version', ''),
                            'extrainfo': port_data.get('extrainfo', '')
                        }
                        
                        if port_data['state'] == 'open':
                            host_info['open_ports'].append(port_info)
                        elif port_data['state'] == 'filtered':
                            host_info['filtered_ports'].append(port_info)
                        else:
                            host_info['closed_ports'] += 1
                
                scan_result['hosts'].append(host_info)
            
            self._log_scan(scan_result)
            return scan_result
            
        except Exception as e:
            logger.error(f"Erro no scan completo: {e}")
            return {
                'target': target,
                'scan_type': 'full_ports',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def scan_vulnerabilities(self, target: str) -> Dict[str, Any]:
        """
        Scan de vulnerabilidades usando NSE scripts
        
        Args:
            target: IP ou hostname
        
        Returns:
            Resultado do scan
        """
        logger.info(f"Iniciando scan de vulnerabilidades em {target}")
        
        try:
            # Scripts NSE para vulnerabilidades comuns
            nse_scripts = [
                'vuln',
                'ssl-enum-ciphers',
                'ssl-cert',
                'http-enum',
                'ftp-anon',
                'smb-vuln*'
            ]
            
            scripts_arg = ','.join(nse_scripts)
            scan_args = f'--script {scripts_arg} --script-args=unsafe=1'
            
            result = self.nm.scan(target, '22,80,443,445,21,25', arguments=scan_args)
            
            scan_result = {
                'target': target,
                'scan_type': 'vulnerability',
                'timestamp': time.time(),
                'vulnerabilities': [],
                'recommendations': []
            }
            
            for host, data in result['scan'].items():
                if 'tcp' in data:
                    for port, port_data in data['tcp'].items():
                        if 'script' in port_data:
                            for script_name, script_output in port_data['script'].items():
                                vuln_info = {
                                    'host': host,
                                    'port': port,
                                    'script': script_name,
                                    'output': script_output,
                                    'severity': self._assess_vulnerability_severity(script_name, script_output)
                                }
                                scan_result['vulnerabilities'].append(vuln_info)
            
            # Gerar recomendações
            scan_result['recommendations'] = self._generate_recommendations(scan_result['vulnerabilities'])
            
            self._log_scan(scan_result)
            return scan_result
            
        except Exception as e:
            logger.error(f"Erro no scan de vulnerabilidades: {e}")
            return {
                'target': target,
                'scan_type': 'vulnerability',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _extract_os_info(self, host_data: Dict) -> Dict[str, str]:
        """Extrair informações do OS"""
        os_info = {'family': '', 'name': '', 'accuracy': ''}
        
        if 'osmatch' in host_data and host_data['osmatch']:
            best_match = host_data['osmatch'][0]
            os_info['name'] = best_match.get('name', '')
            os_info['accuracy'] = best_match.get('accuracy', '')
            
            if 'osclass' in best_match and best_match['osclass']:
                os_info['family'] = best_match['osclass'][0].get('osfamily', '')
        
        return os_info
    
    def _assess_vulnerability_severity(self, script_name: str, output: str) -> str:
        """Avaliar severidade da vulnerabilidade"""
        output_lower = output.lower()
        
        # Crítica
        if any(keyword in output_lower for keyword in ['critical', 'rce', 'remote code', 'unauthenticated']):
            return 'CRITICAL'
        
        # Alta
        if any(keyword in output_lower for keyword in ['high', 'vulnerable', 'exploit', 'backdoor']):
            return 'HIGH'
        
        # Média
        if any(keyword in output_lower for keyword in ['medium', 'weak', 'deprecated', 'insecure']):
            return 'MEDIUM'
        
        # Baixa
        if any(keyword in output_lower for keyword in ['low', 'info', 'disclosure']):
            return 'LOW'
        
        return 'INFO'
    
    def _generate_recommendations(self, vulnerabilities: List[Dict]) -> List[str]:
        """Gerar recomendações baseadas nas vulnerabilidades"""
        recommendations = []
        
        # Analisar vulnerabilidades por tipo
        vuln_types = {}
        for vuln in vulnerabilities:
            script = vuln['script']
            severity = vuln['severity']
            
            if script not in vuln_types:
                vuln_types[script] = []
            vuln_types[script].append(severity)
        
        # Gerar recomendações específicas
        for script, severities in vuln_types.items():
            if 'ssl' in script:
                if any(s in ['CRITICAL', 'HIGH'] for s in severities):
                    recommendations.append('Atualizar configuração SSL/TLS e desabilitar cifras fracas')
            
            elif 'smb' in script:
                if any(s in ['CRITICAL', 'HIGH'] for s in severities):
                    recommendations.append('Aplicar patches de segurança para SMB e desabilitar versões antigas')
            
            elif 'http' in script:
                recommendations.append('Revisar configuração do servidor web e ocultar informações de versão')
            
            elif 'ftp' in script:
                recommendations.append('Desabilitar acesso anônimo FTP e usar FTPS/SFTP')
        
        # Recomendações gerais
        recommendations.extend([
            'Manter todos os sistemas atualizados com patches de segurança',
            'Implementar firewall para restringir acesso a serviços',
            'Monitorar logs de segurança regularmente',
            'Implementar autenticação forte onde apropriado'
        ])
        
        return list(set(recommendations))  # Remover duplicatas
    
    def _log_scan(self, scan_result: Dict[str, Any]):
        """Registrar scan no histórico"""
        self.scan_history.append(scan_result)
        
        # Manter apenas últimos 100 scans
        if len(self.scan_history) > 100:
            self.scan_history.pop(0)
        
        logger.info(f"Scan {scan_result['scan_type']} concluído para {scan_result['target']}")
    
    def get_scan_history(self) -> List[Dict[str, Any]]:
        """Obter histórico de scans"""
        return self.scan_history.copy()

# Funções de conveniência
def run_quick_scan(target: str) -> Dict[str, Any]:
    """
    Executar scan rápido
    
    Args:
        target: Alvo do scan
    
    Returns:
        Resultado do scan
    """
    scanner = SecureScanner()
    
    # Validar alvo
    is_valid, error = scanner.validate_target(target)
    if not is_valid:
        return {
            'error': error,
            'target': target,
            'timestamp': time.time()
        }
    
    return scanner.scan_ports_quick(target)

def run_full_scan(target: str, port_range: str = '1-1000') -> Dict[str, Any]:
    """
    Executar scan completo
    
    Args:
        target: Alvo do scan
        port_range: Range de portas
    
    Returns:
        Resultado do scan
    """
    scanner = SecureScanner()
    
    # Validar alvo
    is_valid, error = scanner.validate_target(target)
    if not is_valid:
        return {
            'error': error,
            'target': target,
            'timestamp': time.time()
        }
    
    return scanner.scan_ports_full(target, port_range)

def run_vulnerability_scan(target: str) -> Dict[str, Any]:
    """
    Executar scan de vulnerabilidades
    
    Args:
        target: Alvo do scan
    
    Returns:
        Resultado do scan
    """
    scanner = SecureScanner()
    
    # Validar alvo
    is_valid, error = scanner.validate_target(target)
    if not is_valid:
        return {
            'error': error,
            'target': target,
            'timestamp': time.time()
        }
    
    return scanner.scan_vulnerabilities(target)

if __name__ == "__main__":
    # Teste do scanner
    print("=== JARVIS Network Scanner Test ===")
    
    scanner = SecureScanner()
    
    # Teste de validação
    print("\nTestando validação de alvos:")
    
    test_targets = ['127.0.0.1', '192.168.1.0/24', '8.8.8.8', '10.0.0.1']
    for target in test_targets:
        is_valid, error = scanner.validate_target(target)
        status = "✅" if is_valid else "❌"
        print(f"{status} {target}: {error if error else 'Válido'}")
    
    # Teste de scan (apenas localhost)
    print("\nTestando scan rápido do localhost:")
    result = run_quick_scan('127.0.0.1')
    
    if 'error' not in result:
        print(f"Hosts encontrados: {len(result['hosts'])}")
        for host in result['hosts']:
            print(f"  {host['ip']}: {host['ports_open']} portas abertas")
    else:
        print(f"Erro: {result['error']}")
    
    print("\nTeste concluído!")