#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - FastAPI Server
Servidor principal com autenticação e integração do System Prompt
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn, os, time, logging, sqlite3, json
from pathlib import Path
import sys

# Adicionar paths
sys.path.append(str(Path(__file__).parent.parent))

from server.auth import create_token_for_agent, verify_token_header
from server.commands_db import CommandsDB
from models.local_model import LocalModelWrapper

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="JARVIS Cyber Security Server", version="1.0.0")

# CORS para interface web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
DB = CommandsDB('server/commands.db')
MODEL = None

# Carregar System Prompt
SYSTEM_PROMPT = ""
try:
    prompt_file = Path(__file__).parent.parent / "docs" / "system_prompt.txt"
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            SYSTEM_PROMPT = f.read()
    else:
        SYSTEM_PROMPT = "Você é JARVIS, um assistente de cibersegurança ética."
except Exception as e:
    logging.warning(f"Erro ao carregar system prompt: {e}")
    SYSTEM_PROMPT = "Você é JARVIS, um assistente de cibersegurança ética."

class CmdRequest(BaseModel):
    agent_id: str
    command_key: str
    params: dict = {}

class AnalysisRequest(BaseModel):
    text: str
    context: str = ""

@app.on_startup
async def startup():
    """Inicializar modelo na inicialização"""
    global MODEL
    try:
        MODEL = LocalModelWrapper()
        logging.info("✅ Modelo carregado com sucesso")
    except Exception as e:
        logging.error(f"❌ Erro ao carregar modelo: {e}")
        MODEL = None

@app.get("/")
def root():
    """Endpoint raiz"""
    return {
        "service": "JARVIS Cyber Security Server",
        "version": "1.0.0",
        "status": "online",
        "time": time.time()
    }

@app.post("/api/command")
def post_command(cmd: CmdRequest, auth=Depends(verify_token_header)):
    """Criar comando para agente"""
    # Verificar se comando é permitido
    if not DB.is_valid_command(cmd.command_key):
        raise HTTPException(status_code=400, detail=f"Comando '{cmd.command_key}' não permitido")
    
    # Verificar parâmetros críticos
    if cmd.command_key in ['scan_quick', 'scan_full'] and 'target' in cmd.params:
        target = cmd.params['target']
        if not DB.is_authorized_target(target):
            raise HTTPException(status_code=403, detail=f"Alvo '{target}' não autorizado")
    
    # Criar comando na fila
    entry = DB.create_command(cmd.agent_id, cmd.command_key, cmd.params, created_by=auth)
    
    logging.info(f"Comando criado: {entry['id']} - {cmd.command_key} para {cmd.agent_id}")
    return {"status": "queued", "id": entry["id"], "command": cmd.command_key}

@app.get("/api/commands/{agent_id}")
def get_commands(agent_id: str, auth=Depends(verify_token_header)):
    """Buscar comandos pendentes para agente"""
    # Verificar se agente pode acessar seus próprios comandos
    if auth != agent_id and auth != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    cmds = DB.get_pending_for_agent(agent_id)
    return {"commands": cmds, "count": len(cmds)}

@app.post("/api/result")
def post_result(payload: dict, auth=Depends(verify_token_header)):
    """Receber resultado de execução do agente"""
    required_fields = ['command_id', 'agent_id', 'result']
    for field in required_fields:
        if field not in payload:
            raise HTTPException(status_code=400, detail=f"Campo obrigatório: {field}")
    
    # Verificar autorização
    if auth != payload['agent_id'] and auth != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    DB.store_result(payload)
    logging.info(f"Resultado armazenado para comando {payload['command_id']}")
    return {"status": "stored"}

@app.post("/api/analyze")
def analyze_text(request: AnalysisRequest):
    """Analisar texto usando IA com System Prompt"""
    if not MODEL:
        raise HTTPException(status_code=503, detail="Modelo não disponível")
    
    try:
        # Construir prompt completo
        full_prompt = f"{SYSTEM_PROMPT}\n\nCONTEXTO: {request.context}\n\nUSER_INPUT:\n{request.text}"
        
        # Gerar resposta
        response = MODEL.chat(full_prompt)
        
        return {
            "response": response,
            "analysis_time": time.time(),
            "model_used": MODEL.get_model_info()
        }
        
    except Exception as e:
        logging.error(f"Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.get("/api/agents")
def list_agents(auth=Depends(verify_token_header)):
    """Listar agentes ativos"""
    if auth != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")
    
    agents = DB.get_active_agents()
    return {"agents": agents}

@app.get("/api/logs")
def get_logs(auth=Depends(verify_token_header)):
    """Obter logs de atividades"""
    if auth != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")
    
    logs = DB.get_recent_logs()
    return {"logs": logs}

@app.post("/api/authorize-target")
def authorize_target(payload: dict, auth=Depends(verify_token_header)):
    """Autorizar novo alvo para scans"""
    if auth != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin")
    
    target = payload.get('target')
    description = payload.get('description', '')
    
    if not target:
        raise HTTPException(status_code=400, detail="Campo 'target' obrigatório")
    
    DB.authorize_target(target, description)
    logging.info(f"Alvo autorizado: {target}")
    return {"status": "authorized", "target": target}

@app.get("/api/authorized-targets")
def get_authorized_targets(auth=Depends(verify_token_header)):
    """Listar alvos autorizados"""
    targets = DB.get_authorized_targets()
    return {"targets": targets}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)