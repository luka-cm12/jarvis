#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging do JARVIS
Configuração centralizada de logs com diferentes níveis e formatação
"""

import logging
import logging.handlers
import os
from datetime import datetime
import colorlog

def setup_logging(log_level="INFO", log_file="logs/jarvis.log"):
    """Configura o sistema de logging do JARVIS"""
    
    # Criar diretório de logs se não existir
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configurar nível de log
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Formatter para arquivo
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formatter colorido para console
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'blue',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Configurar root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Limpar handlers existentes
    logger.handlers.clear()
    
    # Handler para arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Configurar loggers de bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logger

class JarvisLogger:
    """Wrapper personalizado para logging do JARVIS"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def system(self, message):
        """Log para eventos do sistema"""
        self.logger.info(f"🔧 SISTEMA: {message}")
    
    def voice(self, message):
        """Log para eventos de voz"""
        self.logger.info(f"🎤 VOZ: {message}")
    
    def ai(self, message):
        """Log para eventos de IA"""
        self.logger.info(f"🧠 IA: {message}")
    
    def automation(self, message):
        """Log para eventos de automação"""
        self.logger.info(f"🏠 AUTOMAÇÃO: {message}")
    
    def security(self, message):
        """Log para eventos de segurança"""
        self.logger.warning(f"🔒 SEGURANÇA: {message}")
    
    def error(self, message):
        """Log para erros"""
        self.logger.error(f"❌ ERRO: {message}")
    
    def debug(self, message):
        """Log para debug"""
        self.logger.debug(f"🐛 DEBUG: {message}")