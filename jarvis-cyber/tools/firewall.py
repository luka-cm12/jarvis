#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Firewall Management
Gerenciamento seguro de firewall com dry-run e backup
"""

import subprocess
import logging
import platform
import time
import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jarvis.firewall')

class FirewallManager:
    """
    Gerenciador de firewall multiplataforma
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.backup_dir = Path("backups/firewall")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Detectar tipo de firewall
        self.firewall_type = self._detect_firewall()
        logger.info(f"Sistema detectado: {self.system}, Firewall: {self.firewall_type}")
    
    def _detect_firewall(self) -> str:
        """Detectar tipo de firewall disponível"""
        if self.system == "linux":
            # Verificar UFW
            try:
                result = subprocess.run(['which', 'ufw'], capture_output=True)
                if result.returncode == 0:
                    return "ufw"
            except:
                pass
            
            # Verificar iptables
            try:
                result = subprocess.run(['which', 'iptables'], capture_output=True)
                if result.returncode == 0:
                    return "iptables"
            except:
                pass
        
        elif self.system == "windows":
            return "windows"
        
        elif self.system == "darwin":
            return "pf"  # macOS Packet Filter
        
        return "unknown"
    
    def check_firewall_status(self) -> Dict[str, Any]:
        """Verificar status do firewall"""
        logger.info("Verificando status do firewall")
        
        if self.firewall_type == "ufw":
            return self._check_ufw_status()
        elif self.firewall_type == "iptables":
            return self._check_iptables_status()
        elif self.firewall_type == "windows":
            return self._check_windows_firewall_status()
        elif self.firewall_type == "pf":
            return self._check_pf_status()
        else:
            return {
                'status': 'unknown',
                'error': f'Firewall type {self.firewall_type} not supported'
            }
    
    def _check_ufw_status(self) -> Dict[str, Any]:
        """Verificar status do UFW"""
        try:
            # Status geral
            result = subprocess.run(['ufw', 'status', 'verbose'], 
                                  capture_output=True, text=True)
            
            status_info = {
                'firewall_type': 'ufw',
                'enabled': 'Status: active' in result.stdout,
                'rules': [],
                'default_policies': {},
                'raw_output': result.stdout
            }
            
            # Extrair políticas padrão
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Default:' in line:
                    parts = line.split(',')
                    for part in parts:
                        if 'incoming' in part:
                            status_info['default_policies']['incoming'] = part.split()[-1]
                        elif 'outgoing' in part:
                            status_info['default_policies']['outgoing'] = part.split()[-1]
            
            # Extrair regras
            in_rules_section = False
            for line in lines:
                if 'To                         Action      From' in line:
                    in_rules_section = True
                    continue
                
                if in_rules_section and line.strip() and not line.startswith('-'):
                    parts = line.split()
                    if len(parts) >= 3:
                        rule = {
                            'to': parts[0],
                            'action': parts[1],
                            'from': parts[2] if len(parts) > 2 else 'any'
                        }
                        status_info['rules'].append(rule)
            
            return status_info
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_iptables_status(self) -> Dict[str, Any]:
        """Verificar status do iptables"""
        try:
            # Listar regras
            result = subprocess.run(['iptables', '-L', '-n', '-v'], 
                                  capture_output=True, text=True)
            
            return {
                'firewall_type': 'iptables',
                'enabled': True,  # iptables está sempre "ativo"
                'raw_output': result.stdout,
                'rules_count': result.stdout.count('Chain')
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_windows_firewall_status(self) -> Dict[str, Any]:
        """Verificar status do Windows Firewall"""
        try:
            # Verificar status dos perfis
            cmd = ['powershell', '-Command', 
                  'Get-NetFirewallProfile | Select-Object Name,Enabled | ConvertTo-Json']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                profiles = json.loads(result.stdout)
                return {
                    'firewall_type': 'windows',
                    'profiles': profiles,
                    'enabled': any(p['Enabled'] for p in profiles)
                }
            else:
                return {'status': 'error', 'error': result.stderr}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_pf_status(self) -> Dict[str, Any]:
        """Verificar status do PF (macOS)"""
        try:
            result = subprocess.run(['pfctl', '-si'], 
                                  capture_output=True, text=True)
            
            return {
                'firewall_type': 'pf',
                'enabled': 'Status: Enabled' in result.stdout,
                'raw_output': result.stdout
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def backup_current_config(self) -> str:
        """Fazer backup da configuração atual"""
        timestamp = int(time.time())
        backup_file = self.backup_dir / f"firewall_backup_{timestamp}.txt"
        
        logger.info(f"Fazendo backup da configuração em {backup_file}")
        
        try:
            config = self.check_firewall_status()
            
            with open(backup_file, 'w') as f:
                f.write(f"# Firewall Backup - {time.ctime()}\n")
                f.write(f"# System: {self.system}\n")
                f.write(f"# Firewall Type: {self.firewall_type}\n\n")
                f.write(json.dumps(config, indent=2))
            
            logger.info(f"Backup criado: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def apply_basic_hardening(self, dry_run: bool = True) -> Dict[str, Any]:
        """Aplicar hardening básico do firewall"""
        logger.info(f"Aplicando hardening básico (dry_run={dry_run})")
        
        if not dry_run:
            backup_file = self.backup_current_config()
        else:
            backup_file = None
        
        if self.firewall_type == "ufw":
            return self._apply_ufw_hardening(dry_run, backup_file)
        elif self.firewall_type == "windows":
            return self._apply_windows_hardening(dry_run, backup_file)
        else:
            return {
                'status': 'error',
                'error': f'Hardening não implementado para {self.firewall_type}'
            }
    
    def _apply_ufw_hardening(self, dry_run: bool, backup_file: Optional[str]) -> Dict[str, Any]:
        """Aplicar hardening do UFW"""
        commands = [
            # Reset (apenas se especificado)
            # ('ufw', '--force', 'reset'),
            
            # Políticas padrão
            ('ufw', 'default', 'deny', 'incoming'),
            ('ufw', 'default', 'allow', 'outgoing'),
            
            # Regras básicas
            ('ufw', 'allow', 'ssh'),
            ('ufw', 'allow', 'out', '53'),  # DNS
            ('ufw', 'allow', 'out', '80'),  # HTTP
            ('ufw', 'allow', 'out', '443'), # HTTPS
            ('ufw', 'allow', 'out', '123'), # NTP
            
            # Habilitar firewall
            ('ufw', '--force', 'enable')
        ]
        
        results = []
        
        for cmd in commands:
            if dry_run:
                results.append({
                    'command': ' '.join(cmd),
                    'status': 'DRY_RUN',
                    'output': 'Comando seria executado'
                })
            else:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    results.append({
                        'command': ' '.join(cmd),
                        'status': 'SUCCESS' if result.returncode == 0 else 'ERROR',
                        'output': result.stdout,
                        'error': result.stderr
                    })
                except Exception as e:
                    results.append({
                        'command': ' '.join(cmd),
                        'status': 'ERROR',
                        'error': str(e)
                    })
        
        return {
            'firewall_type': 'ufw',
            'dry_run': dry_run,
            'backup_file': backup_file,
            'commands_executed': len(results),
            'results': results
        }
    
    def _apply_windows_hardening(self, dry_run: bool, backup_file: Optional[str]) -> Dict[str, Any]:
        """Aplicar hardening do Windows Firewall"""
        commands = [
            # Habilitar todos os perfis
            'Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True',
            
            # Políticas padrão
            'Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultInboundAction Block',
            'Set-NetFirewallProfile -Profile Domain,Public,Private -DefaultOutboundAction Allow',
            
            # Regras básicas
            'New-NetFirewallRule -DisplayName "Allow SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow',
            'New-NetFirewallRule -DisplayName "Allow RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow',
            'New-NetFirewallRule -DisplayName "Allow HTTP Out" -Direction Outbound -Protocol TCP -LocalPort 80 -Action Allow',
            'New-NetFirewallRule -DisplayName "Allow HTTPS Out" -Direction Outbound -Protocol TCP -LocalPort 443 -Action Allow'
        ]
        
        results = []
        
        for cmd in commands:
            full_cmd = ['powershell', '-Command', cmd]
            
            if dry_run:
                results.append({
                    'command': cmd,
                    'status': 'DRY_RUN',
                    'output': 'Comando seria executado'
                })
            else:
                try:
                    result = subprocess.run(full_cmd, capture_output=True, text=True)
                    results.append({
                        'command': cmd,
                        'status': 'SUCCESS' if result.returncode == 0 else 'ERROR',
                        'output': result.stdout,
                        'error': result.stderr
                    })
                except Exception as e:
                    results.append({
                        'command': cmd,
                        'status': 'ERROR',
                        'error': str(e)
                    })
        
        return {
            'firewall_type': 'windows',
            'dry_run': dry_run,
            'backup_file': backup_file,
            'commands_executed': len(results),
            'results': results
        }
    
    def add_rule(self, rule_config: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Adicionar regra personalizada"""
        logger.info(f"Adicionando regra: {rule_config} (dry_run={dry_run})")
        
        if self.firewall_type == "ufw":
            return self._add_ufw_rule(rule_config, dry_run)
        elif self.firewall_type == "windows":
            return self._add_windows_rule(rule_config, dry_run)
        else:
            return {
                'status': 'error',
                'error': f'Adição de regras não implementada para {self.firewall_type}'
            }
    
    def _add_ufw_rule(self, rule_config: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Adicionar regra UFW"""
        try:
            # Construir comando UFW
            cmd = ['ufw']
            
            if rule_config.get('action') == 'allow':
                cmd.append('allow')
            elif rule_config.get('action') == 'deny':
                cmd.append('deny')
            else:
                return {'status': 'error', 'error': 'Ação inválida'}
            
            if rule_config.get('direction') == 'out':
                cmd.append('out')
            
            if 'port' in rule_config:
                cmd.append(str(rule_config['port']))
            
            if 'protocol' in rule_config:
                cmd.append(rule_config['protocol'])
            
            if dry_run:
                return {
                    'command': ' '.join(cmd),
                    'status': 'DRY_RUN',
                    'output': 'Regra seria adicionada'
                }
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return {
                    'command': ' '.join(cmd),
                    'status': 'SUCCESS' if result.returncode == 0 else 'ERROR',
                    'output': result.stdout,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _add_windows_rule(self, rule_config: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Adicionar regra Windows"""
        try:
            # Construir comando PowerShell
            cmd_parts = ['New-NetFirewallRule']
            
            if 'name' in rule_config:
                cmd_parts.append(f'-DisplayName "{rule_config["name"]}"')
            
            if 'direction' in rule_config:
                cmd_parts.append(f'-Direction {rule_config["direction"].title()}')
            
            if 'protocol' in rule_config:
                cmd_parts.append(f'-Protocol {rule_config["protocol"].upper()}')
            
            if 'port' in rule_config:
                cmd_parts.append(f'-LocalPort {rule_config["port"]}')
            
            if 'action' in rule_config:
                action = 'Allow' if rule_config['action'] == 'allow' else 'Block'
                cmd_parts.append(f'-Action {action}')
            
            cmd = ' '.join(cmd_parts)
            full_cmd = ['powershell', '-Command', cmd]
            
            if dry_run:
                return {
                    'command': cmd,
                    'status': 'DRY_RUN',
                    'output': 'Regra seria adicionada'
                }
            else:
                result = subprocess.run(full_cmd, capture_output=True, text=True)
                return {
                    'command': cmd,
                    'status': 'SUCCESS' if result.returncode == 0 else 'ERROR',
                    'output': result.stdout,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

# Funções de conveniência
def check_firewall_status() -> Dict[str, Any]:
    """Verificar status do firewall"""
    manager = FirewallManager()
    return manager.check_firewall_status()

def apply_basic_hardening(dry_run: bool = True) -> Dict[str, Any]:
    """Aplicar hardening básico"""
    manager = FirewallManager()
    return manager.apply_basic_hardening(dry_run)

def ufw_dry_run_check() -> List[str]:
    """Mostrar regras recomendadas para UFW"""
    return [
        "ufw default deny incoming",
        "ufw default allow outgoing",
        "ufw allow ssh",
        "ufw allow out 53",   # DNS
        "ufw allow out 80",   # HTTP
        "ufw allow out 443",  # HTTPS
        "ufw --force enable"
    ]

def ufw_apply(recommended_rules: List[str]) -> Dict[str, Any]:
    """Aplicar regras UFW recomendadas"""
    results = []
    
    for rule in recommended_rules:
        try:
            cmd = rule.split()
            result = subprocess.run(cmd, capture_output=True, text=True)
            results.append({
                'rule': rule,
                'status': 'SUCCESS' if result.returncode == 0 else 'ERROR',
                'output': result.stdout,
                'error': result.stderr
            })
        except Exception as e:
            results.append({
                'rule': rule,
                'status': 'ERROR',
                'error': str(e)
            })
    
    return {'status': 'applied', 'results': results}

if __name__ == "__main__":
    # Teste do sistema de firewall
    print("=== JARVIS Firewall Manager Test ===")
    
    manager = FirewallManager()
    print(f"Sistema: {manager.system}")
    print(f"Firewall: {manager.firewall_type}")
    
    # Verificar status
    print("\nVerificando status do firewall:")
    status = manager.check_firewall_status()
    
    if 'error' not in status:
        print(f"Tipo: {status.get('firewall_type', 'unknown')}")
        print(f"Ativo: {status.get('enabled', False)}")
    else:
        print(f"Erro: {status['error']}")
    
    # Teste de hardening (dry-run)
    print("\nTestando hardening (dry-run):")
    hardening_result = manager.apply_basic_hardening(dry_run=True)
    
    if 'error' not in hardening_result:
        print(f"Comandos a executar: {hardening_result['commands_executed']}")
        for result in hardening_result['results'][:3]:  # Mostrar apenas os primeiros
            print(f"  {result['command']}: {result['status']}")
    else:
        print(f"Erro: {hardening_result['error']}")
    
    print("\nTeste concluído!")