#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Configurações do JARVIS
Responsável por carregar e validar as configurações do sistema
"""

import json
import os
from pathlib import Path
import logging

class ConfigManager:
    def __init__(self, config_path="config/config.json"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Carrega as configurações do arquivo JSON"""
        try:
            if not self.config_path.exists():
                self.logger.error(f"Arquivo de configuração não encontrado: {self.config_path}")
                self.logger.info("Copie config.example.json para config.json e configure suas credenciais")
                return None
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.logger.info("Configurações carregadas com sucesso")
            return self._validate_config(config)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return None
    
    def _validate_config(self, config):
        """Valida as configurações carregadas"""
        required_sections = ['jarvis', 'audio', 'ai', 'logging']
        
        for section in required_sections:
            if section not in config:
                self.logger.warning(f"Seção '{section}' não encontrada na configuração")
                config[section] = {}
        
        # Validações específicas
        if not config['ai'].get('openai_api_key') or config['ai']['openai_api_key'] == 'sua-api-key-aqui':
            self.logger.warning("OpenAI API key não configurada - funcionalidade de IA limitada")
            
        return config
    
    def save_config(self, config):
        """Salva as configurações no arquivo JSON"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.logger.info("Configurações salvas com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False