#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funções auxiliares para ferramentas do JARVIS
Versões simplificadas para testes rápidos
"""

def run_quick_scan(target: str) -> dict:
    """
    Scan rápido simplificado para teste
    """
    import socket
    import threading
    from ipaddress import ip_address, AddressValueError
    
    try:
        # Validar IP
        ip_address(target)
        ip_target = target
    except AddressValueError:
        try:
            # Tentar resolver hostname
            ip_target = socket.gethostbyname(target)
        except socket.gaierror:
            return {'error': f'Não foi possível resolver: {target}'}
    
    # Portas comuns para teste
    common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080]
    open_ports = []
    
    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip_target, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    
    # Scan paralelo
    threads = []
    for port in common_ports:
        thread = threading.Thread(target=scan_port, args=(port,))
        threads.append(thread)
        thread.start()
    
    # Aguardar conclusão
    for thread in threads:
        thread.join()
    
    return {
        'hosts': [{
            'ip': ip_target,
            'open_ports': open_ports,
            'status': 'online' if open_ports else 'filtered'
        }]
    }

def run_quick_assessment() -> dict:
    """
    Avaliação de segurança simplificada
    """
    import os
    import platform
    import subprocess
    
    score = 50  # Score base
    recommendations = []
    
    # Verificar sistema operacional
    system = platform.system().lower()
    
    if system == 'windows':
        # Verificar Windows Defender
        try:
            result = subprocess.run(['powershell', 'Get-MpComputerStatus'], 
                                  capture_output=True, text=True, timeout=10)
            if 'True' in result.stdout:
                score += 20
            else:
                recommendations.append("Ativar Windows Defender")
        except:
            recommendations.append("Verificar status do antivírus")
        
        # Verificar firewall
        try:
            result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                                  capture_output=True, text=True, timeout=10)
            if 'ON' in result.stdout:
                score += 15
            else:
                recommendations.append("Ativar firewall do Windows")
        except:
            recommendations.append("Verificar configuração do firewall")
            
    elif system == 'linux':
        # Verificar UFW
        try:
            result = subprocess.run(['ufw', 'status'], 
                                  capture_output=True, text=True, timeout=5)
            if 'active' in result.stdout.lower():
                score += 15
            else:
                recommendations.append("Ativar UFW firewall")
        except:
            recommendations.append("Instalar e configurar firewall")
        
        # Verificar atualizações
        if os.path.exists('/usr/bin/apt'):
            recommendations.append("Verificar atualizações do sistema")
        
        score += 10  # Bonus por usar Linux
        
    else:  # macOS ou outros
        score += 5
        recommendations.append("Verificar configurações de segurança do sistema")
    
    # Verificações gerais
    if os.path.exists(os.path.expanduser('~/.ssh')):
        score += 5
        recommendations.append("Revisar chaves SSH")
    
    # Limitar score
    score = min(score, 100)
    
    # Adicionar recomendações baseadas no score
    if score < 70:
        recommendations.insert(0, "Implementar autenticação de dois fatores")
        recommendations.insert(1, "Usar senhas fortes e gerenciador de senhas")
    
    return {
        'overall_score': score,
        'recommendations': recommendations[:5],  # Máximo 5 recomendações
        'system': system,
        'status': 'completed'
    }

# Teste das funções se executado diretamente
if __name__ == "__main__":
    print("Testando scanner...")
    result = run_quick_scan("127.0.0.1")
    print(f"Resultado: {result}")
    
    print("\nTestando avaliação...")
    assessment = run_quick_assessment()
    print(f"Score: {assessment['overall_score']}")
    print(f"Recomendações: {assessment['recommendations']}")