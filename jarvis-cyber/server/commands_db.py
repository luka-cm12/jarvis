#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Commands Database
Sistema de banco de dados SQLite para comandos, resultados e logs
"""

import sqlite3
import time
import json
import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)

class CommandsDB:
    """Gerenciador de banco de dados para comandos e logs"""
    
    def __init__(self, path: str = 'server/commands.db'):
        """
        Inicializar banco de dados
        
        Args:
            path: Caminho para arquivo SQLite
        """
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        
        self.db_path = path
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Permitir acesso por nome
        
        self._create_tables()
        self._setup_authorized_targets()
        
    def _create_tables(self):
        """Criar tabelas do banco de dados"""
        cursor = self.conn.cursor()
        
        # Tabela de comandos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                command_key TEXT NOT NULL,
                params TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by TEXT NOT NULL,
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                priority INTEGER DEFAULT 5
            )
        ''')
        
        # Tabela de resultados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id INTEGER NOT NULL,
                agent_id TEXT NOT NULL,
                result TEXT NOT NULL,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                created_at REAL NOT NULL,
                FOREIGN KEY (command_id) REFERENCES commands (id)
            )
        ''')
        
        # Tabela de alvos autorizados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS authorized_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT UNIQUE NOT NULL,
                description TEXT,
                authorized_by TEXT NOT NULL,
                authorized_at REAL NOT NULL,
                active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Tabela de agentes ativos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT UNIQUE NOT NULL,
                hostname TEXT,
                ip_address TEXT,
                last_seen REAL NOT NULL,
                status TEXT DEFAULT 'active',
                capabilities TEXT
            )
        ''')
        
        # Tabela de logs de segurança
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                agent_id TEXT,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        self.conn.commit()
        logging.info("Tabelas do banco de dados criadas/verificadas")
    
    def _setup_authorized_targets(self):
        """Configurar alvos autorizados padrão"""
        default_targets = [
            ('127.0.0.1', 'Localhost - sempre permitido'),
            ('localhost', 'Localhost hostname'),
            ('10.0.0.0/8', 'Rede privada RFC 1918'),
            ('192.168.0.0/16', 'Rede privada RFC 1918'),
            ('172.16.0.0/12', 'Rede privada RFC 1918')
        ]
        
        for target, description in default_targets:
            try:
                self.authorize_target(target, description, 'system')
            except sqlite3.IntegrityError:
                # Já existe
                pass
    
    def create_command(self, agent_id: str, command_key: str, params: dict, 
                      created_by: str = 'admin', priority: int = 5) -> dict:
        """
        Criar novo comando na fila
        
        Args:
            agent_id: ID do agente
            command_key: Chave do comando
            params: Parâmetros do comando
            created_by: Quem criou o comando
            priority: Prioridade (1=alta, 5=normal, 10=baixa)
        
        Returns:
            Informações do comando criado
        """
        cursor = self.conn.cursor()
        now = time.time()
        
        cursor.execute('''
            INSERT INTO commands (agent_id, command_key, params, created_by, created_at, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (agent_id, command_key, json.dumps(params), created_by, now, priority))
        
        command_id = cursor.lastrowid
        self.conn.commit()
        
        # Log de segurança
        self.log_security_event(
            agent_id, 'command_created', 'info',
            f'Comando {command_key} criado para agente {agent_id}',
            {'command_id': command_id, 'created_by': created_by}
        )
        
        return {
            "id": command_id,
            "agent_id": agent_id,
            "command_key": command_key,
            "params": params,
            "created_at": now
        }
    
    def get_pending_for_agent(self, agent_id: str) -> List[dict]:
        """
        Obter comandos pendentes para agente
        
        Args:
            agent_id: ID do agente
        
        Returns:
            Lista de comandos pendentes
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT id, command_key, params, priority, created_at
            FROM commands 
            WHERE agent_id = ? AND status = 'pending'
            ORDER BY priority ASC, created_at ASC
        ''', (agent_id,))
        
        commands = []
        for row in cursor.fetchall():
            commands.append({
                "id": row['id'],
                "command_key": row['command_key'],
                "params": json.loads(row['params']),
                "priority": row['priority'],
                "created_at": row['created_at']
            })
        
        # Atualizar agente como ativo
        self.update_agent_status(agent_id, 'active')
        
        return commands
    
    def is_valid_command(self, command_key: str) -> bool:
        """
        Verificar se comando é válido (whitelist)
        
        Args:
            command_key: Chave do comando
        
        Returns:
            True se comando é permitido
        """
        # Whitelist de comandos permitidos
        allowed_commands = {
            'uptime',           # Tempo de atividade do sistema
            'status',           # Status do sistema
            'disk_usage',       # Uso do disco
            'memory_usage',     # Uso da memória
            'scan_quick',       # Scan rápido de portas
            'scan_full',        # Scan completo
            'apply_hardening',  # Aplicar hardening básico
            'check_firewall',   # Verificar firewall
            'backup_config',    # Backup de configurações
            'update_system',    # Atualizar sistema (dry-run)
            'check_logs',       # Verificar logs de segurança
            'scan_vulnerabilities'  # Scan de vulnerabilidades
        }
        
        return command_key in allowed_commands
    
    def is_authorized_target(self, target: str) -> bool:
        """
        Verificar se alvo é autorizado para scans
        
        Args:
            target: IP ou hostname do alvo
        
        Returns:
            True se alvo é autorizado
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count FROM authorized_targets 
            WHERE target = ? AND active = 1
        ''', (target,))
        
        result = cursor.fetchone()
        return result['count'] > 0
    
    def authorize_target(self, target: str, description: str = '', authorized_by: str = 'admin'):
        """
        Autorizar novo alvo
        
        Args:
            target: IP ou hostname
            description: Descrição do alvo
            authorized_by: Quem autorizou
        """
        cursor = self.conn.cursor()
        now = time.time()
        
        cursor.execute('''
            INSERT OR REPLACE INTO authorized_targets 
            (target, description, authorized_by, authorized_at, active)
            VALUES (?, ?, ?, ?, 1)
        ''', (target, description, authorized_by, now))
        
        self.conn.commit()
        
        # Log de segurança
        self.log_security_event(
            None, 'target_authorized', 'warning',
            f'Alvo {target} autorizado para scans',
            {'authorized_by': authorized_by, 'description': description}
        )
    
    def get_authorized_targets(self) -> List[dict]:
        """
        Obter lista de alvos autorizados
        
        Returns:
            Lista de alvos autorizados
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT target, description, authorized_by, authorized_at
            FROM authorized_targets 
            WHERE active = 1
            ORDER BY authorized_at DESC
        ''', ())
        
        targets = []
        for row in cursor.fetchall():
            targets.append({
                "target": row['target'],
                "description": row['description'],
                "authorized_by": row['authorized_by'],
                "authorized_at": row['authorized_at']
            })
        
        return targets
    
    def store_result(self, payload: dict):
        """
        Armazenar resultado de execução
        
        Args:
            payload: Dados do resultado
        """
        cursor = self.conn.cursor()
        now = time.time()
        
        command_id = payload.get('command_id')
        agent_id = payload.get('agent_id')
        result = payload.get('result', {})
        success = result.get('ok', False)
        error_message = result.get('error', result.get('reason', ''))
        
        # Inserir resultado
        cursor.execute('''
            INSERT INTO results (command_id, agent_id, result, success, error_message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (command_id, agent_id, json.dumps(result), success, error_message, now))
        
        # Atualizar status do comando
        status = 'completed' if success else 'failed'
        cursor.execute('''
            UPDATE commands 
            SET status = ?, completed_at = ?
            WHERE id = ?
        ''', (status, now, command_id))
        
        self.conn.commit()
        
        # Log de segurança
        severity = 'info' if success else 'error'
        self.log_security_event(
            agent_id, 'command_completed', severity,
            f'Comando {command_id} concluído com status: {status}',
            {'success': success, 'error': error_message}
        )
    
    def update_agent_status(self, agent_id: str, status: str = 'active', 
                          hostname: str = None, ip_address: str = None):
        """
        Atualizar status do agente
        
        Args:
            agent_id: ID do agente
            status: Status do agente
            hostname: Nome do host
            ip_address: Endereço IP
        """
        cursor = self.conn.cursor()
        now = time.time()
        
        cursor.execute('''
            INSERT OR REPLACE INTO active_agents 
            (agent_id, hostname, ip_address, last_seen, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (agent_id, hostname, ip_address, now, status))
        
        self.conn.commit()
    
    def get_active_agents(self) -> List[dict]:
        """
        Obter lista de agentes ativos
        
        Returns:
            Lista de agentes
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT agent_id, hostname, ip_address, last_seen, status
            FROM active_agents
            WHERE last_seen > ? 
            ORDER BY last_seen DESC
        ''', (time.time() - 3600,))  # Última hora
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "agent_id": row['agent_id'],
                "hostname": row['hostname'],
                "ip_address": row['ip_address'],
                "last_seen": row['last_seen'],
                "status": row['status']
            })
        
        return agents
    
    def log_security_event(self, agent_id: Optional[str], event_type: str, 
                          severity: str, message: str, details: dict = None):
        """
        Registrar evento de segurança
        
        Args:
            agent_id: ID do agente (opcional)
            event_type: Tipo do evento
            severity: Severidade (info, warning, error, critical)
            message: Mensagem do evento
            details: Detalhes adicionais
        """
        cursor = self.conn.cursor()
        now = time.time()
        
        cursor.execute('''
            INSERT INTO security_logs 
            (timestamp, agent_id, event_type, severity, message, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (now, agent_id, event_type, severity, message, 
              json.dumps(details) if details else None))
        
        self.conn.commit()
        
        # Log também no sistema
        log_level = {
            'info': logging.INFO,
            'warning': logging.WARNING, 
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(severity, logging.INFO)
        
        logging.log(log_level, f"[{event_type}] {message} (Agent: {agent_id})")
    
    def get_recent_logs(self, limit: int = 100) -> List[dict]:
        """
        Obter logs recentes
        
        Args:
            limit: Limite de logs
        
        Returns:
            Lista de logs
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, agent_id, event_type, severity, message, details
            FROM security_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            logs.append({
                "timestamp": row['timestamp'],
                "agent_id": row['agent_id'],
                "event_type": row['event_type'],
                "severity": row['severity'],
                "message": row['message'],
                "details": json.loads(row['details']) if row['details'] else None
            })
        
        return logs
    
    def close(self):
        """Fechar conexão com banco"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Destrutor"""
        self.close()

if __name__ == "__main__":
    # Teste do sistema
    db = CommandsDB(':memory:')  # Banco em memória para teste
    
    print("=== Teste do Commands DB ===")
    
    # Autorizar alguns alvos
    db.authorize_target('192.168.1.100', 'Servidor de teste')
    db.authorize_target('10.0.0.50', 'Workstation desenvolvimento')
    
    # Criar alguns comandos
    cmd1 = db.create_command('agent-001', 'scan_quick', {'target': '192.168.1.100'})
    cmd2 = db.create_command('agent-001', 'uptime', {})
    
    print(f"Comandos criados: {cmd1['id']}, {cmd2['id']}")
    
    # Buscar comandos pendentes
    pending = db.get_pending_for_agent('agent-001')
    print(f"Comandos pendentes: {len(pending)}")
    
    # Simular resultado
    db.store_result({
        'command_id': cmd1['id'],
        'agent_id': 'agent-001',
        'result': {'ok': True, 'output': 'Scan completed'}
    })
    
    # Verificar logs
    logs = db.get_recent_logs(5)
    print(f"Logs recentes: {len(logs)}")
    
    print("Teste concluído com sucesso!")