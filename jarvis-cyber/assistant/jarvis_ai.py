#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Just A Rather Very Intelligent System
Assistente Virtual Completo inspirado no Homem de Ferro
"""

import os
import subprocess
import json
import platform
from datetime import datetime
from pathlib import Path

class JarvisAssistant:
    """Assistente virtual JARVIS completo"""
    
    def __init__(self):
        self.name = "JARVIS"
        self.version = "1.0.0"
        self.personality = "formal_british"
        self.user_name = "Sir"
        self.context_memory = []
        self.projects_created = []
        
    def greet(self, user_name: str = None) -> str:
        """Saudação do JARVIS"""
        if user_name:
            self.user_name = user_name
            
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = f"Bom dia, {self.user_name}."
        elif hour < 18:
            greeting = f"Boa tarde, {self.user_name}."
        else:
            greeting = f"Boa noite, {self.user_name}."
            
        return f"{greeting} JARVIS às suas ordens. Como posso ajudá-lo hoje?"
    
    def process_command(self, command: str) -> dict:
        """Processar comando do usuário"""
        command_lower = command.lower()
        
        # Comandos de criação
        if any(word in command_lower for word in ['criar', 'create', 'gerar', 'generate', 'desenvolver', 'build']):
            return self.handle_creation_command(command)
        
        # Comandos de informação
        elif any(word in command_lower for word in ['status', 'como está', 'relatório', 'report']):
            return self.get_system_status()
        
        # Comandos de ajuda
        elif any(word in command_lower for word in ['ajuda', 'help', 'o que você pode', 'capabilities']):
            return self.show_capabilities()
        
        # Comandos de automação
        elif any(word in command_lower for word in ['automatizar', 'automate', 'executar', 'run']):
            return self.handle_automation_command(command)
        
        # Conversação geral
        else:
            return self.general_conversation(command)
    
    def handle_creation_command(self, command: str) -> dict:
        """Lidar com comandos de criação"""
        command_lower = command.lower()
        
        # Criar website
        if 'website' in command_lower or 'site' in command_lower or 'web' in command_lower:
            return self.create_website_project(command)
        
        # Criar API
        elif 'api' in command_lower or 'backend' in command_lower:
            return self.create_api_project(command)
        
        # Criar app mobile
        elif 'app' in command_lower or 'mobile' in command_lower or 'android' in command_lower:
            return self.create_mobile_project(command)
        
        # Criar script
        elif 'script' in command_lower or 'automação' in command_lower:
            return self.create_script(command)
        
        # Criar banco de dados
        elif 'database' in command_lower or 'banco de dados' in command_lower:
            return self.create_database_schema(command)
        
        # Criar IA/ML
        elif 'ia' in command_lower or 'machine learning' in command_lower or 'ai' in command_lower:
            return self.create_ai_project(command)
        
        else:
            return {
                'response': f"Entendido, {self.user_name}. Poderia especificar que tipo de projeto deseja criar? Posso criar websites, APIs, apps mobile, scripts, bancos de dados ou projetos de IA.",
                'action': 'clarification_needed',
                'suggestions': ['website', 'api', 'mobile app', 'script', 'database', 'ai project']
            }
    
    def create_website_project(self, description: str) -> dict:
        """Criar projeto de website"""
        project_name = self.extract_project_name(description) or "jarvis-website"
        
        structure = {
            'type': 'website',
            'name': project_name,
            'files': {
                'index.html': self.generate_html_template(),
                'style.css': self.generate_css_template(),
                'script.js': self.generate_js_template(),
                'README.md': f"# {project_name}\n\nWebsite criado pelo JARVIS\n"
            }
        }
        
        # Criar estrutura de pastas
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        
        for filename, content in structure['files'].items():
            (project_path / filename).write_text(content, encoding='utf-8')
        
        self.projects_created.append(structure)
        
        return {
            'response': f"Website '{project_name}' criado com sucesso, {self.user_name}. Estrutura HTML, CSS e JavaScript implementada. O projeto está pronto para ser personalizado.",
            'action': 'project_created',
            'project': structure,
            'path': str(project_path.absolute())
        }
    
    def create_api_project(self, description: str) -> dict:
        """Criar projeto de API REST"""
        project_name = self.extract_project_name(description) or "jarvis-api"
        
        structure = {
            'type': 'api',
            'name': project_name,
            'files': {
                'app.py': self.generate_fastapi_template(),
                'requirements.txt': 'fastapi==0.109.0\nuvicorn==0.27.0\npydantic==2.5.3\n',
                'models.py': self.generate_models_template(),
                'README.md': f"# {project_name}\n\nAPI REST criada pelo JARVIS\n\n## Executar\n```bash\npip install -r requirements.txt\nuvicorn app:app --reload\n```\n"
            }
        }
        
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        
        for filename, content in structure['files'].items():
            (project_path / filename).write_text(content, encoding='utf-8')
        
        self.projects_created.append(structure)
        
        return {
            'response': f"API REST '{project_name}' criada com sucesso, {self.user_name}. FastAPI configurado com endpoints básicos. Pronto para desenvolvimento.",
            'action': 'project_created',
            'project': structure,
            'path': str(project_path.absolute()),
            'next_steps': [
                'cd ' + project_name,
                'pip install -r requirements.txt',
                'uvicorn app:app --reload'
            ]
        }
    
    def create_mobile_project(self, description: str) -> dict:
        """Criar projeto mobile"""
        project_name = self.extract_project_name(description) or "jarvis-mobile-app"
        
        return {
            'response': f"Entendido, {self.user_name}. Para criar um app mobile, recomendo usar React Native ou Flutter. Posso gerar a estrutura básica de um projeto React Native com expo. Deseja prosseguir?",
            'action': 'suggestion',
            'suggested_command': f'npx create-expo-app {project_name}'
        }
    
    def create_script(self, description: str) -> dict:
        """Criar script de automação"""
        script_name = self.extract_project_name(description) or "automation_script"
        
        script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Automação criado pelo JARVIS
Descrição: {description}
"""

import os
import sys
from datetime import datetime

def main():
    """Função principal do script"""
    print(f"[{{datetime.now()}}] Script iniciado pelo JARVIS")
    
    # Seu código aqui
    print("Executando automação...")
    
    print(f"[{{datetime.now()}}] Script concluído")

if __name__ == "__main__":
    main()
'''
        
        script_path = Path(f"{script_name}.py")
        script_path.write_text(script_content, encoding='utf-8')
        
        return {
            'response': f"Script '{script_name}.py' criado com sucesso, {self.user_name}. Pronto para ser personalizado com sua lógica de automação.",
            'action': 'file_created',
            'file': str(script_path.absolute())
        }
    
    def create_database_schema(self, description: str) -> dict:
        """Criar schema de banco de dados"""
        schema_name = self.extract_project_name(description) or "database_schema"
        
        sql_content = f'''-- Schema de Banco de Dados criado pelo JARVIS
-- Descrição: {description}
-- Data: {datetime.now().isoformat()}

CREATE DATABASE IF NOT EXISTS {schema_name};
USE {schema_name};

-- Tabela de Usuários
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de Logs
CREATE TABLE logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100),
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Índices para performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
'''
        
        schema_path = Path(f"{schema_name}.sql")
        schema_path.write_text(sql_content, encoding='utf-8')
        
        return {
            'response': f"Schema de banco de dados '{schema_name}.sql' criado, {self.user_name}. Estrutura básica com tabelas de usuários e logs implementada.",
            'action': 'file_created',
            'file': str(schema_path.absolute())
        }
    
    def create_ai_project(self, description: str) -> dict:
        """Criar projeto de IA/ML"""
        project_name = self.extract_project_name(description) or "jarvis-ai-project"
        
        structure = {
            'type': 'ai_ml',
            'name': project_name,
            'files': {
                'train.py': self.generate_ml_training_template(),
                'model.py': self.generate_ml_model_template(),
                'requirements.txt': 'torch==2.1.0\ntransformers==4.35.0\nscikit-learn==1.3.2\npandas==2.1.3\nnumpy==1.26.2\n',
                'README.md': f"# {project_name}\n\nProjeto de IA/ML criado pelo JARVIS\n"
            }
        }
        
        project_path = Path(project_name)
        project_path.mkdir(exist_ok=True)
        
        for filename, content in structure['files'].items():
            (project_path / filename).write_text(content, encoding='utf-8')
        
        return {
            'response': f"Projeto de IA '{project_name}' criado com sucesso, {self.user_name}. Estrutura básica de Machine Learning com PyTorch implementada.",
            'action': 'project_created',
            'project': structure,
            'path': str(project_path.absolute())
        }
    
    def handle_automation_command(self, command: str) -> dict:
        """Executar comandos de automação"""
        return {
            'response': f"Preparado para executar automação, {self.user_name}. Especifique a tarefa que deseja automatizar.",
            'action': 'automation_ready'
        }
    
    def get_system_status(self) -> dict:
        """Obter status do sistema"""
        system_info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'python_version': platform.python_version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        
        status_text = f"""Status do Sistema, {self.user_name}:
        
🖥️  Sistema Operacional: {system_info['os']}
🐍 Python: {system_info['python_version']}
⚙️  Processador: {system_info['processor']}
📊 Projetos Criados: {len(self.projects_created)}
🕐 Horário: {datetime.now().strftime('%H:%M:%S')}

Todos os sistemas operacionais."""
        
        return {
            'response': status_text,
            'action': 'status_report',
            'data': system_info
        }
    
    def show_capabilities(self) -> dict:
        """Mostrar capacidades do JARVIS"""
        capabilities = f"""Minhas capacidades, {self.user_name}:

🏗️  CRIAÇÃO DE PROJETOS:
   • Websites (HTML, CSS, JavaScript)
   • APIs REST (FastAPI, Flask)
   • Apps Mobile (React Native)
   • Scripts de Automação (Python)
   • Schemas de Banco de Dados (SQL)
   • Projetos de IA/ML (PyTorch)

🤖 AUTOMAÇÃO:
   • Execução de tarefas automatizadas
   • Gerenciamento de processos
   • Integração com sistemas

🔒 SEGURANÇA:
   • Testes de penetração ética
   • Análise de vulnerabilidades
   • Hardening de sistemas

💬 ASSISTÊNCIA:
   • Conversação natural
   • Sugestões inteligentes
   • Geração de código

Como posso ajudá-lo, {self.user_name}?"""
        
        return {
            'response': capabilities,
            'action': 'capabilities_shown'
        }
    
    def general_conversation(self, message: str) -> dict:
        """Conversação geral com IA"""
        self.context_memory.append({
            'user': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Respostas contextuais
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['obrigado', 'thanks', 'valeu']):
            response = f"Sempre às ordens, {self.user_name}."
        elif any(word in message_lower for word in ['quem é você', 'who are you', 'o que é jarvis']):
            response = f"Sou JARVIS - Just A Rather Very Intelligent System. Seu assistente pessoal para desenvolvimento, automação e segurança cibernética, {self.user_name}."
        elif any(word in message_lower for word in ['olá', 'oi', 'hello', 'hi']):
            response = self.greet()
        else:
            response = f"Entendido, {self.user_name}. Como posso ajudá-lo com isso?"
        
        return {
            'response': response,
            'action': 'conversation',
            'context': len(self.context_memory)
        }
    
    def extract_project_name(self, text: str) -> str:
        """Extrair nome do projeto do texto"""
        # Procurar por padrões comuns
        keywords = ['chamado', 'named', 'nome', 'name', 'projeto', 'project']
        
        for keyword in keywords:
            if keyword in text.lower():
                parts = text.lower().split(keyword)
                if len(parts) > 1:
                    name_part = parts[1].strip().split()[0]
                    return name_part.replace('"', '').replace("'", '')
        
        return None
    
    # Templates de código
    def generate_html_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS Project</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Projeto criado pelo JARVIS</h1>
        <p>Sistema pronto para personalização.</p>
    </div>
    <script src="script.js"></script>
</body>
</html>'''
    
    def generate_css_template(self) -> str:
        return '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    color: #ffffff;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.container {
    text-align: center;
    padding: 40px;
    background: rgba(0, 212, 255, 0.1);
    border: 2px solid #00d4ff;
    border-radius: 15px;
}

h1 {
    color: #00d4ff;
    margin-bottom: 20px;
}'''
    
    def generate_js_template(self) -> str:
        return '''// JavaScript criado pelo JARVIS
console.log('JARVIS Project initialized');

document.addEventListener('DOMContentLoaded', function() {
    console.log('System ready');
});'''
    
    def generate_fastapi_template(self) -> str:
        return '''from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="JARVIS API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "JARVIS API - Sistema Operacional"}

@app.get("/status")
def get_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "jarvis": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)'''
    
    def generate_models_template(self) -> str:
        return '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    created_at: Optional[datetime] = None

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float'''
    
    def generate_ml_training_template(self) -> str:
        return '''import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from model import SimpleModel

def train_model(epochs=10):
    """Treinar modelo"""
    print("JARVIS: Iniciando treinamento...")
    
    model = SimpleModel()
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    for epoch in range(epochs):
        print(f"Epoch {epoch+1}/{epochs}")
        # Seu código de treinamento aqui
        
    print("JARVIS: Treinamento concluído")
    return model

if __name__ == "__main__":
    train_model()'''
    
    def generate_ml_model_template(self) -> str:
        return '''import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    """Modelo simples criado pelo JARVIS"""
    
    def __init__(self, input_size=784, hidden_size=128, num_classes=10):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out'''

# Funções de conveniência
def create_jarvis_assistant():
    """Criar instância do assistente JARVIS"""
    return JarvisAssistant()

def process_jarvis_command(command: str, user_name: str = "Sir") -> dict:
    """Processar comando do JARVIS"""
    assistant = JarvisAssistant()
    assistant.user_name = user_name
    return assistant.process_command(command)

if __name__ == "__main__":
    # Teste do assistente
    jarvis = JarvisAssistant()
    print(jarvis.greet("Tony"))
    
    # Teste de criação de website
    result = jarvis.process_command("JARVIS, criar um website chamado meu-portfolio")
    print(result['response'])