#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - System Hardening
Ferramentas de hardening de sistema para múltiplas plataformas
"""

import subprocess
import platform
import logging
import json
import os
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jarvis.hardening')

class SystemHardening:
    """
    Sistema de hardening multiplataforma com verificações de segurança
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.backup_dir = Path("backups/hardening")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Sistema detectado: {self.system}")
    
    def run_security_assessment(self) -> Dict[str, Any]:
        """
        Executar avaliação completa de segurança
        
        Returns:
            Relatório de segurança
        """
        logger.info("Iniciando avaliação de segurança")
        
        assessment = {
            'timestamp': time.time(),
            'system': self.system,
            'checks': {},
            'recommendations': [],
            'overall_score': 0
        }
        
        if self.system == "linux":
            assessment['checks'] = self._assess_linux_security()
        elif self.system == "windows":
            assessment['checks'] = self._assess_windows_security()
        elif self.system == "darwin":
            assessment['checks'] = self._assess_macos_security()
        else:
            assessment['checks'] = {'error': f'Sistema {self.system} não suportado'}
        
        # Calcular score geral
        assessment['overall_score'] = self._calculate_security_score(assessment['checks'])
        
        # Gerar recomendações
        assessment['recommendations'] = self._generate_recommendations(assessment['checks'])
        
        return assessment
    
    def _assess_linux_security(self) -> Dict[str, Any]:
        """Avaliar segurança do Linux"""
        checks = {}
        
        # Verificar atualizações
        checks['system_updates'] = self._check_linux_updates()
        
        # Verificar firewall
        checks['firewall_status'] = self._check_firewall_status()
        
        # Verificar serviços
        checks['running_services'] = self._check_running_services()
        
        # Verificar permissões de arquivos
        checks['file_permissions'] = self._check_critical_file_permissions()
        
        # Verificar usuários e grupos
        checks['user_accounts'] = self._check_user_accounts()
        
        # Verificar configurações SSH
        checks['ssh_config'] = self._check_ssh_configuration()
        
        # Verificar logs de segurança
        checks['security_logs'] = self._check_security_logs()
        
        return checks
    
    def _assess_windows_security(self) -> Dict[str, Any]:
        """Avaliar segurança do Windows"""
        checks = {}
        
        # Verificar Windows Update
        checks['windows_update'] = self._check_windows_updates()
        
        # Verificar Windows Defender
        checks['antivirus_status'] = self._check_windows_defender()
        
        # Verificar firewall
        checks['firewall_status'] = self._check_windows_firewall()
        
        # Verificar UAC
        checks['uac_status'] = self._check_uac_status()
        
        # Verificar serviços
        checks['running_services'] = self._check_windows_services()
        
        # Verificar usuários
        checks['user_accounts'] = self._check_windows_users()
        
        return checks
    
    def _assess_macos_security(self) -> Dict[str, Any]:
        """Avaliar segurança do macOS"""
        checks = {}
        
        # Verificar atualizações
        checks['system_updates'] = self._check_macos_updates()
        
        # Verificar firewall
        checks['firewall_status'] = self._check_macos_firewall()
        
        # Verificar Gatekeeper
        checks['gatekeeper_status'] = self._check_gatekeeper()
        
        # Verificar SIP
        checks['sip_status'] = self._check_system_integrity_protection()
        
        return checks
    
    def _check_linux_updates(self) -> Dict[str, Any]:
        """Verificar atualizações disponíveis no Linux"""
        try:
            # Detectar gerenciador de pacotes
            if os.path.exists('/usr/bin/apt'):
                return self._check_apt_updates()
            elif os.path.exists('/usr/bin/yum'):
                return self._check_yum_updates()
            elif os.path.exists('/usr/bin/dnf'):
                return self._check_dnf_updates()
            else:
                return {'status': 'unknown', 'manager': 'unknown'}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_apt_updates(self) -> Dict[str, Any]:
        """Verificar atualizações APT"""
        try:
            # Atualizar lista de pacotes
            subprocess.run(['apt', 'update'], capture_output=True, check=True)
            
            # Verificar atualizações disponíveis
            result = subprocess.run(['apt', 'list', '--upgradable'], 
                                  capture_output=True, text=True)
            
            upgradable_lines = [line for line in result.stdout.split('\n') 
                              if line and not line.startswith('Listing')]
            
            return {
                'status': 'good' if len(upgradable_lines) == 0 else 'warning',
                'manager': 'apt',
                'updates_available': len(upgradable_lines),
                'packages': upgradable_lines[:10]  # Primeiros 10
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_firewall_status(self) -> Dict[str, Any]:
        """Verificar status do firewall"""
        try:
            # Verificar UFW
            try:
                result = subprocess.run(['ufw', 'status'], 
                                      capture_output=True, text=True)
                active = 'Status: active' in result.stdout
                return {
                    'status': 'good' if active else 'critical',
                    'type': 'ufw',
                    'enabled': active
                }
            except FileNotFoundError:
                pass
            
            # Verificar iptables
            try:
                result = subprocess.run(['iptables', '-L'], 
                                      capture_output=True, text=True)
                rules_count = result.stdout.count('Chain')
                return {
                    'status': 'warning',
                    'type': 'iptables',
                    'rules_count': rules_count
                }
            except FileNotFoundError:
                pass
            
            return {'status': 'critical', 'type': 'none', 'enabled': False}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_running_services(self) -> Dict[str, Any]:
        """Verificar serviços em execução"""
        try:
            if self.system == "linux":
                result = subprocess.run(['systemctl', 'list-units', '--type=service', '--state=running'],
                                      capture_output=True, text=True)
                
                lines = result.stdout.split('\n')[1:-1]  # Remover header e footer
                services = []
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            services.append(parts[0])
                
                # Verificar serviços críticos
                critical_services = ['ssh', 'sshd', 'telnet', 'ftp', 'rsh']
                risky_services = [s for s in services if any(cs in s for cs in critical_services)]
                
                return {
                    'status': 'warning' if risky_services else 'good',
                    'total_services': len(services),
                    'risky_services': risky_services,
                    'all_services': services[:20]  # Primeiros 20
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_critical_file_permissions(self) -> Dict[str, Any]:
        """Verificar permissões de arquivos críticos"""
        critical_files = [
            '/etc/passwd',
            '/etc/shadow',
            '/etc/sudoers',
            '/etc/ssh/sshd_config'
        ]
        
        file_checks = []
        
        for file_path in critical_files:
            try:
                stat_info = os.stat(file_path)
                permissions = oct(stat_info.st_mode)[-3:]
                
                # Verificar se as permissões são seguras
                secure_perms = {
                    '/etc/passwd': '644',
                    '/etc/shadow': '640',
                    '/etc/sudoers': '440',
                    '/etc/ssh/sshd_config': '644'
                }
                
                expected = secure_perms.get(file_path, '644')
                is_secure = permissions == expected
                
                file_checks.append({
                    'file': file_path,
                    'permissions': permissions,
                    'expected': expected,
                    'secure': is_secure
                })
                
            except FileNotFoundError:
                file_checks.append({
                    'file': file_path,
                    'status': 'not_found'
                })
            except Exception as e:
                file_checks.append({
                    'file': file_path,
                    'error': str(e)
                })
        
        insecure_files = [f for f in file_checks if not f.get('secure', True)]
        
        return {
            'status': 'critical' if insecure_files else 'good',
            'checked_files': len(file_checks),
            'insecure_files': len(insecure_files),
            'details': file_checks
        }
    
    def _check_user_accounts(self) -> Dict[str, Any]:
        """Verificar contas de usuário"""
        try:
            with open('/etc/passwd', 'r') as f:
                passwd_lines = f.readlines()
            
            users = []
            for line in passwd_lines:
                parts = line.strip().split(':')
                if len(parts) >= 6:
                    users.append({
                        'username': parts[0],
                        'uid': int(parts[2]),
                        'gid': int(parts[3]),
                        'home': parts[5],
                        'shell': parts[6]
                    })
            
            # Verificar usuários com UID 0 (root)
            root_users = [u for u in users if u['uid'] == 0]
            
            # Verificar usuários com shell interativo
            interactive_shells = ['/bin/bash', '/bin/sh', '/bin/zsh', '/bin/fish']
            interactive_users = [u for u in users if u['shell'] in interactive_shells and u['uid'] >= 1000]
            
            return {
                'status': 'warning' if len(root_users) > 1 else 'good',
                'total_users': len(users),
                'root_users': len(root_users),
                'interactive_users': len(interactive_users),
                'details': {
                    'root_accounts': [u['username'] for u in root_users],
                    'regular_users': [u['username'] for u in interactive_users]
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_ssh_configuration(self) -> Dict[str, Any]:
        """Verificar configuração SSH"""
        config_file = '/etc/ssh/sshd_config'
        
        try:
            with open(config_file, 'r') as f:
                config_lines = f.readlines()
            
            config = {}
            for line in config_lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if len(parts) >= 2:
                        config[parts[0].lower()] = ' '.join(parts[1:])
            
            # Verificar configurações de segurança
            security_checks = {
                'root_login': config.get('permitrootlogin', 'yes').lower() == 'no',
                'password_auth': config.get('passwordauthentication', 'yes').lower() == 'no',
                'empty_passwords': config.get('permitemptypasswords', 'no').lower() == 'no',
                'protocol_2': config.get('protocol', '2') == '2',
                'x11_forwarding': config.get('x11forwarding', 'yes').lower() == 'no'
            }
            
            secure_count = sum(security_checks.values())
            total_checks = len(security_checks)
            
            return {
                'status': 'good' if secure_count >= 4 else 'warning' if secure_count >= 2 else 'critical',
                'secure_settings': secure_count,
                'total_checks': total_checks,
                'details': security_checks
            }
            
        except FileNotFoundError:
            return {'status': 'info', 'message': 'SSH não instalado'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_windows_updates(self) -> Dict[str, Any]:
        """Verificar Windows Update"""
        try:
            cmd = [
                'powershell', '-Command',
                'Get-WUList | Measure-Object | Select-Object Count'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'status': 'good',
                    'updates_available': 0,
                    'message': 'Sistema atualizado'
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Não foi possível verificar atualizações'
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_windows_defender(self) -> Dict[str, Any]:
        """Verificar Windows Defender"""
        try:
            cmd = [
                'powershell', '-Command',
                'Get-MpPreference | Select-Object DisableRealtimeMonitoring'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            enabled = 'False' in result.stdout
            
            return {
                'status': 'good' if enabled else 'critical',
                'enabled': enabled,
                'real_time_protection': enabled
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_security_score(self, checks: Dict[str, Any]) -> int:
        """Calcular score geral de segurança"""
        if not checks or 'error' in checks:
            return 0
        
        status_scores = {
            'good': 100,
            'warning': 60,
            'critical': 20,
            'error': 0,
            'info': 80
        }
        
        scores = []
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict) and 'status' in check_data:
                status = check_data['status']
                scores.append(status_scores.get(status, 50))
        
        return int(sum(scores) / len(scores)) if scores else 0
    
    def _generate_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Gerar recomendações baseadas nos checks"""
        recommendations = []
        
        for check_name, check_data in checks.items():
            if isinstance(check_data, dict):
                status = check_data.get('status')
                
                if status == 'critical':
                    if check_name == 'firewall_status':
                        recommendations.append("🔥 CRÍTICO: Ativar firewall do sistema")
                    elif check_name == 'file_permissions':
                        recommendations.append("🔒 CRÍTICO: Corrigir permissões de arquivos críticos")
                    elif check_name == 'antivirus_status':
                        recommendations.append("🛡️ CRÍTICO: Ativar proteção antivírus")
                
                elif status == 'warning':
                    if check_name == 'system_updates':
                        recommendations.append("📦 Instalar atualizações de segurança disponíveis")
                    elif check_name == 'running_services':
                        recommendations.append("⚠️ Revisar serviços desnecessários em execução")
                    elif check_name == 'ssh_config':
                        recommendations.append("🔐 Endurecer configuração SSH")
        
        # Recomendações gerais
        recommendations.extend([
            "🔄 Configurar backup automático de dados importantes",
            "📊 Implementar monitoramento de logs de segurança",
            "👥 Revisar contas de usuário e permissões",
            "🔍 Executar scans de vulnerabilidade regularmente"
        ])
        
        return recommendations[:10]  # Máximo 10 recomendações

# Funções de conveniência
def run_quick_assessment() -> Dict[str, Any]:
    """Executar avaliação rápida de segurança"""
    hardening = SystemHardening()
    return hardening.run_security_assessment()

def get_security_score() -> int:
    """Obter score de segurança atual"""
    assessment = run_quick_assessment()
    return assessment.get('overall_score', 0)

def apply_basic_hardening(dry_run: bool = True) -> Dict[str, Any]:
    """Aplicar hardening básico"""
    hardening = SystemHardening()
    
    recommendations = {
        'linux': [
            'sudo ufw enable',
            'sudo apt update && sudo apt upgrade -y',
            'sudo systemctl disable telnet',
            'sudo chmod 640 /etc/shadow'
        ],
        'windows': [
            'Set-NetFirewallProfile -Enabled True',
            'Set-MpPreference -DisableRealtimeMonitoring $false',
            'Install-WindowsUpdate -AcceptAll -AutoReboot'
        ]
    }
    
    system = platform.system().lower()
    commands = recommendations.get(system, [])
    
    if dry_run:
        return {
            'system': system,
            'dry_run': True,
            'recommended_commands': commands,
            'message': 'Execute os comandos manualmente para aplicar hardening'
        }
    else:
        return {
            'system': system,
            'dry_run': False,
            'message': 'Hardening automático não implementado por segurança'
        }

if __name__ == "__main__":
    # Teste do sistema de hardening
    print("=== JARVIS System Hardening Test ===")
    
    hardening = SystemHardening()
    print(f"Sistema: {hardening.system}")
    
    # Executar avaliação de segurança
    print("\nExecutando avaliação de segurança...")
    assessment = hardening.run_security_assessment()
    
    print(f"Score de segurança: {assessment['overall_score']}/100")
    print(f"Checks realizados: {len(assessment['checks'])}")
    
    # Mostrar recomendações
    print("\nRecomendações:")
    for i, rec in enumerate(assessment['recommendations'][:5], 1):
        print(f"{i}. {rec}")
    
    # Mostrar status dos checks principais
    print("\nStatus dos checks:")
    for check_name, check_data in list(assessment['checks'].items())[:5]:
        if isinstance(check_data, dict) and 'status' in check_data:
            status_emoji = {
                'good': '✅',
                'warning': '⚠️',
                'critical': '❌',
                'error': '💥',
                'info': 'ℹ️'
            }
            emoji = status_emoji.get(check_data['status'], '❓')
            print(f"  {emoji} {check_name}: {check_data['status']}")
    
    print("\nAvaliação concluída!")