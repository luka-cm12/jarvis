#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Authentication System
Sistema de autenticação JWT para agentes e administradores
"""

import jwt
import os
import time
import hashlib
import secrets
from fastapi import Header, HTTPException
from typing import Optional

SECRET = os.getenv("JARVIS_SECRET", "troque_por_seguro_em_producao")
ALGORITHM = "HS256"

# Usuários administrativos (em produção, use banco de dados)
ADMIN_USERS = {
    "admin": {
        "password_hash": "admin123",  # Trocar em produção
        "role": "admin",
        "permissions": ["all"]
    }
}

def create_token_for_agent(agent_id: str, expires: int = 3600, role: str = "agent") -> str:
    """
    Criar token JWT para agente
    
    Args:
        agent_id: ID único do agente
        expires: Tempo de expiração em segundos
        role: Papel do agente (agent, admin)
    
    Returns:
        Token JWT codificado
    """
    now = time.time()
    payload = {
        "sub": agent_id,
        "role": role,
        "iat": now,
        "exp": now + expires,
        "jti": secrets.token_hex(8)  # Token ID único
    }
    
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def create_admin_token(username: str, password: str, expires: int = 7200) -> str:
    """
    Criar token para administrador
    
    Args:
        username: Nome do usuário admin
        password: Senha do admin
        expires: Expiração em segundos
    
    Returns:
        Token JWT ou levanta exceção
    """
    if username not in ADMIN_USERS:
        raise ValueError("Usuário não encontrado")
    
    user = ADMIN_USERS[username]
    # Em produção, usar hash apropriado (bcrypt, scrypt, etc.)
    if password != user["password_hash"]:
        raise ValueError("Senha incorreta")
    
    return create_token_for_agent(username, expires, "admin")

def verify_token(token: str) -> dict:
    """
    Verificar e decodificar token JWT
    
    Args:
        token: Token JWT
    
    Returns:
        Payload decodificado
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        
        # Verificar expiração
        if payload.get("exp", 0) < time.time():
            raise jwt.ExpiredSignatureError("Token expirado")
        
        return payload
        
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Token inválido: {str(e)}")

def verify_token_header(authorization: Optional[str] = Header(None)) -> str:
    """
    Verificar token no header Authorization
    Dependency para FastAPI
    
    Args:
        authorization: Header Authorization
    
    Returns:
        Subject (agent_id ou username) do token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Token de autorização obrigatório")
    
    try:
        # Formato esperado: "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Formato de autorização inválido")
        
        payload = verify_token(token)
        return payload["sub"]
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de autorização inválido")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

def get_token_info(token: str) -> dict:
    """
    Obter informações detalhadas do token
    
    Args:
        token: Token JWT
    
    Returns:
        Informações do token
    """
    try:
        payload = verify_token(token)
        return {
            "subject": payload.get("sub"),
            "role": payload.get("role", "agent"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "token_id": payload.get("jti"),
            "valid": True
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def generate_agent_credentials(agent_id: str) -> dict:
    """
    Gerar credenciais para novo agente
    
    Args:
        agent_id: ID do agente
    
    Returns:
        Credenciais do agente
    """
    token = create_token_for_agent(agent_id, expires=86400)  # 24 horas
    
    return {
        "agent_id": agent_id,
        "token": token,
        "expires_in": 86400,
        "server_url": os.getenv("JARVIS_SERVER", "http://localhost:8000"),
        "instructions": {
            "environment_vars": {
                "AGENT_ID": agent_id,
                "AGENT_TOKEN": token,
                "JARVIS_SERVER": "http://localhost:8000"
            },
            "startup_command": "python agent/agent.py"
        }
    }

if __name__ == "__main__":
    # Exemplo de uso
    print("=== JARVIS Auth System Test ===")
    
    # Criar token de agente
    agent_token = create_token_for_agent("agent-001")
    print(f"Agent Token: {agent_token}")
    
    # Criar token de admin
    try:
        admin_token = create_admin_token("admin", "admin123")
        print(f"Admin Token: {admin_token}")
    except ValueError as e:
        print(f"Admin Token Error: {e}")
    
    # Verificar token
    info = get_token_info(agent_token)
    print(f"Token Info: {info}")
    
    # Gerar credenciais completas
    creds = generate_agent_credentials("test-agent")
    print(f"Agent Credentials: {creds}")