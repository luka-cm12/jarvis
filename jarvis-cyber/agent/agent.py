#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Secure Agent
Agente seguro com polling, whitelist e execução controlada
"""

import os
import sys
import time
import requests
import logging
import subprocess
import json
import socket
import platform
from typing import Dict, Any, Optional
from pathlib import Path

# Adicionar path para tools
sys.path.append(str(Path(__file__).parent.parent))

# Configurações do agente
SERVER = os.getenv("JARVIS_SERVER", "http://localhost:8000")
TOKEN = os.getenv("AGENT_TOKEN", "token_de_teste")
AGENT_ID = os.getenv("AGENT_ID", "agent-001")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger('jarvis.agent')

# Whitelist de comandos permitidos
COMMAND_WHITELIST = {
    "uptime": {
        "command": "uptime" if platform.system() != "Windows" else "powershell -c \"(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime\"",
        "timeout": 10,
        "safe": True
    },
    "status": {
        "command": "systemctl status" if platform.system() == "Linux" else "sc query",
        "timeout": 15,
        "safe": True
    },
    "disk_usage": {
        "command": "df -h" if platform.system() != "Windows" else "powershell -c \"Get-WmiObject -Class Win32_LogicalDisk | Select-Object Size,FreeSpace,DeviceID\"",
        "timeout": 10,
        "safe": True
    },
    "memory_usage": {
        "command": "free -h" if platform.system() == "Linux" else "powershell -c \"Get-WmiObject -Class Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum\"",
        "timeout": 10,
        "safe": True
    },
    "scan_quick": {
        "handler": "handle_scan",
        "timeout": 60,
        "safe": False,  # Requer verificação de alvo
        "requires_target": True
    },
    "scan_full": {
        "handler": "handle_scan",
        "timeout": 300,
        "safe": False,
        "requires_target": True
    },
    "apply_hardening": {
        "handler": "handle_hardening",
        "timeout": 120,
        "safe": False,  # Altera configurações
        "requires_confirmation": True
    },
    "check_firewall": {
        "handler": "handle_firewall_check",
        "timeout": 30,
        "safe": True
    },
    "check_logs": {
        "handler": "handle_log_check",
        "timeout": 30,
        "safe": True
    }
}

class SecureAgent:
    """Agente seguro para execução de comandos autorizados"""
    
    def __init__(self):
        self.server_url = SERVER
        self.token = TOKEN
        self.agent_id = AGENT_ID
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': f'JARVIS-Agent/{self.agent_id}'
        })
        
        # Informações do sistema
        self.hostname = socket.gethostname()
        self.platform = platform.system()
        
        # Alvos autorizados (carregados do servidor)
        self.authorized_targets = set()
        
        logger.info(f"Agente {self.agent_id} inicializado em {self.hostname} ({self.platform})")
    
    def load_authorized_targets(self) -> bool:
        """
        Carregar lista de alvos autorizados do servidor
        
        Returns:
            True se carregou com sucesso
        """
        try:
            url = f"{self.server_url}/api/authorized-targets"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.authorized_targets = {target['target'] for target in data['targets']}
            
            logger.info(f"Carregados {len(self.authorized_targets)} alvos autorizados")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar alvos autorizados: {e}")
            return False
    
    def poll_commands(self) -> list:
        """
        Buscar comandos pendentes no servidor
        
        Returns:
            Lista de comandos pendentes
        """
        try:
            url = f"{self.server_url}/api/commands/{self.agent_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            commands = data.get('commands', [])
            
            if commands:
                logger.info(f"Recebidos {len(commands)} comandos pendentes")
            
            return commands
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar comandos: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado ao buscar comandos: {e}")
            return []
    
    def validate_command(self, command: dict) -> tuple[bool, str]:
        """
        Validar comando antes da execução
        
        Args:
            command: Comando a ser validado
        
        Returns:
            (is_valid, error_message)
        """
        command_key = command.get('command_key')
        params = command.get('params', {})
        
        # Verificar se comando está na whitelist
        if command_key not in COMMAND_WHITELIST:
            return False, f"Comando '{command_key}' não permitido"
        
        cmd_config = COMMAND_WHITELIST[command_key]
        
        # Verificar se requer alvo e se está autorizado
        if cmd_config.get('requires_target', False):
            target = params.get('target')
            if not target:
                return False, "Comando requer parâmetro 'target'"
            
            if target not in self.authorized_targets:
                return False, f"Alvo '{target}' não autorizado"
        
        return True, ""
    
    def execute_command(self, command: dict) -> dict:
        """
        Executar comando de forma segura
        
        Args:
            command: Comando a ser executado
        
        Returns:
            Resultado da execução
        """
        command_key = command['command_key']
        params = command.get('params', {})
        cmd_config = COMMAND_WHITELIST[command_key]
        
        logger.info(f"Executando comando: {command_key}")
        
        try:
            # Verificar se tem handler customizado
            if 'handler' in cmd_config:
                handler_name = cmd_config['handler']
                handler = getattr(self, handler_name, None)
                
                if handler:
                    return handler(params)
                else:
                    return {
                        'ok': False,
                        'error': f"Handler '{handler_name}' não encontrado"
                    }
            
            # Execução de comando do sistema
            elif 'command' in cmd_config:
                return self.execute_system_command(
                    cmd_config['command'],
                    cmd_config.get('timeout', 30)
                )
            
            else:
                return {
                    'ok': False,
                    'error': 'Configuração de comando inválida'
                }
                
        except Exception as e:
            logger.error(f"Erro ao executar comando {command_key}: {e}")
            return {
                'ok': False,
                'error': str(e)
            }
    
    def execute_system_command(self, cmd: str, timeout: int = 30) -> dict:
        """
        Executar comando do sistema
        
        Args:
            cmd: Comando a executar
            timeout: Timeout em segundos
        
        Returns:
            Resultado da execução
        """
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            return {
                'ok': True,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'ok': False,
                'error': f'Comando expirou após {timeout} segundos'
            }
        except Exception as e:
            return {
                'ok': False,
                'error': str(e)
            }
    
    def handle_scan(self, params: dict) -> dict:
        """
        Handler para comandos de scan
        
        Args:
            params: Parâmetros do scan
        
        Returns:
            Resultado do scan
        """
        try:
            from tools.scanner import run_quick_scan, run_full_scan
            
            target = params.get('target')
            scan_type = params.get('type', 'quick')
            
            logger.info(f"Iniciando scan {scan_type} em {target}")
            
            if scan_type == 'full':
                result = run_full_scan(target)
            else:
                result = run_quick_scan(target)
            
            return {
                'ok': True,
                'scan_type': scan_type,
                'target': target,
                'result': result
            }
            
        except ImportError:
            return {
                'ok': False,
                'error': 'Módulo de scanner não disponível'
            }
        except Exception as e:
            return {
                'ok': False,
                'error': str(e)
            }
    
    def handle_hardening(self, params: dict) -> dict:
        """
        Handler para hardening do sistema
        
        Args:
            params: Parâmetros do hardening
        
        Returns:
            Resultado do hardening
        """
        try:
            from tools.hardening import apply_basic_hardening
            
            dry_run = params.get('dry_run', True)  # Padrão: apenas simular
            
            logger.info(f"Aplicando hardening (dry_run={dry_run})")
            
            result = apply_basic_hardening(params, dry_run=dry_run)
            
            return {
                'ok': True,
                'dry_run': dry_run,
                'result': result
            }
            
        except ImportError:
            return {
                'ok': False,
                'error': 'Módulo de hardening não disponível'
            }
        except Exception as e:
            return {
                'ok': False,
                'error': str(e)
            }
    
    def handle_firewall_check(self, params: dict) -> dict:
        """
        Handler para verificar firewall
        
        Args:
            params: Parâmetros da verificação
        
        Returns:
            Status do firewall
        """
        try:
            from tools.firewall import check_firewall_status
            
            result = check_firewall_status()
            
            return {
                'ok': True,
                'firewall_status': result
            }
            
        except ImportError:
            return {
                'ok': False,
                'error': 'Módulo de firewall não disponível'
            }
        except Exception as e:
            return {
                'ok': False,
                'error': str(e)
            }
    
    def handle_log_check(self, params: dict) -> dict:
        """
        Handler para verificar logs de segurança
        
        Args:
            params: Parâmetros da verificação
        
        Returns:
            Análise dos logs
        """
        try:
            lines = params.get('lines', 100)
            log_type = params.get('type', 'security')
            
            if self.platform == "Linux":
                if log_type == 'security':
                    cmd = f"tail -n {lines} /var/log/auth.log"
                else:
                    cmd = f"tail -n {lines} /var/log/syslog"
            else:
                # Windows - usar PowerShell para logs de eventos
                cmd = f"powershell -c \"Get-EventLog -LogName Security -Newest {lines}\""
            
            result = self.execute_system_command(cmd, timeout=30)
            
            return {
                'ok': True,
                'log_type': log_type,
                'lines_requested': lines,
                'output': result.get('output', '')
            }
            
        except Exception as e:
            return {
                'ok': False,
                'error': str(e)
            }
    
    def post_result(self, command_id: int, result: dict):
        """
        Enviar resultado para o servidor
        
        Args:
            command_id: ID do comando
            result: Resultado da execução
        """
        try:
            url = f"{self.server_url}/api/result"
            payload = {
                'command_id': command_id,
                'agent_id': self.agent_id,
                'result': result,
                'hostname': self.hostname,
                'timestamp': time.time()
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Resultado enviado para comando {command_id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar resultado: {e}")
    
    def run(self):
        """
        Loop principal do agente
        """
        logger.info(f"Iniciando agente {self.agent_id}")
        
        # Carregar alvos autorizados
        self.load_authorized_targets()
        
        retry_count = 0
        
        while True:
            try:
                # Buscar comandos pendentes
                commands = self.poll_commands()
                
                for command in commands:
                    command_id = command.get('id')
                    
                    # Validar comando
                    is_valid, error_msg = self.validate_command(command)
                    
                    if not is_valid:
                        logger.warning(f"Comando inválido {command_id}: {error_msg}")
                        self.post_result(command_id, {
                            'ok': False,
                            'error': error_msg,
                            'validation_failed': True
                        })
                        continue
                    
                    # Executar comando
                    result = self.execute_command(command)
                    
                    # Enviar resultado
                    self.post_result(command_id, result)
                
                # Reset retry counter em caso de sucesso
                retry_count = 0
                
            except KeyboardInterrupt:
                logger.info("Agente interrompido pelo usuário")
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Erro no loop principal (tentativa {retry_count}): {e}")
                
                if retry_count >= MAX_RETRIES:
                    logger.critical(f"Máximo de tentativas excedido. Encerrando agente.")
                    break
                
                # Backoff exponencial
                sleep_time = min(POLL_INTERVAL * (2 ** retry_count), 60)
                logger.info(f"Aguardando {sleep_time} segundos antes de tentar novamente...")
                time.sleep(sleep_time)
                continue
            
            # Aguardar próximo poll
            time.sleep(POLL_INTERVAL)
        
        logger.info("Agente encerrado")

def main():
    """Função principal"""
    print("=== JARVIS Cyber Security Agent ===")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Server: {SERVER}")
    print(f"Platform: {platform.system()}")
    print("====================================\n")
    
    agent = SecureAgent()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\ud83d\uded1 Agente encerrado pelo usuário")
    except Exception as e:
        print(f"\u274c Erro crítico: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())