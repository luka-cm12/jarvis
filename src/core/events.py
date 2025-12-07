#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Eventos do JARVIS
Gerenciamento centralizado de eventos para comunicação entre módulos
"""

import threading
from collections import defaultdict
import logging
from core.logger import JarvisLogger

class EventManager:
    """Gerenciador de eventos singleton para comunicação entre módulos"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = JarvisLogger(__name__)
            self._listeners = defaultdict(list)
            self._lock = threading.RLock()
            self.initialized = True
    
    @classmethod
    def get_instance(cls):
        """Retorna a instância singleton"""
        return cls()
    
    def subscribe(self, event_type, callback):
        """Inscreve um callback para um tipo de evento"""
        with self._lock:
            self._listeners[event_type].append(callback)
        self.logger.debug(f"Callback inscrito para evento '{event_type}'")
    
    def unsubscribe(self, event_type, callback):
        """Remove um callback de um tipo de evento"""
        with self._lock:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
        self.logger.debug(f"Callback removido do evento '{event_type}'")
    
    def emit(self, event_type, data=None):
        """Emite um evento para todos os listeners"""
        with self._lock:
            listeners = self._listeners[event_type].copy()
        
        if listeners:
            self.logger.debug(f"Emitindo evento '{event_type}' para {len(listeners)} listeners")
            
            for callback in listeners:
                try:
                    # Executar callback em thread separada para não bloquear
                    thread = threading.Thread(target=self._safe_callback, args=(callback, event_type, data))
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    self.logger.error(f"Erro ao executar callback para '{event_type}': {e}")
    
    def _safe_callback(self, callback, event_type, data):
        """Executa callback com tratamento de erro"""
        try:
            callback(data)
        except Exception as e:
            self.logger.error(f"Erro no callback do evento '{event_type}': {e}")
    
    @classmethod
    def emit_event(cls, event_type, data=None):
        """Método de classe para emitir eventos facilmente"""
        instance = cls.get_instance()
        instance.emit(event_type, data)
    
    def clear_listeners(self, event_type=None):
        """Remove todos os listeners de um tipo ou todos os tipos"""
        with self._lock:
            if event_type:
                self._listeners[event_type].clear()
            else:
                self._listeners.clear()

# Eventos padrão do sistema
class Events:
    """Constantes para tipos de eventos do JARVIS"""
    
    # Eventos de voz
    WAKE_WORD_DETECTED = 'wake_word_detected'
    VOICE_COMMAND = 'voice_command'
    VOICE_RESPONSE = 'voice_response'
    
    # Eventos do sistema
    SYSTEM_STARTUP = 'system_startup'
    SYSTEM_SHUTDOWN = 'system_shutdown'
    SYSTEM_ERROR = 'system_error'
    
    # Eventos de IA
    AI_THINKING = 'ai_thinking'
    AI_RESPONSE = 'ai_response'
    AI_ERROR = 'ai_error'
    
    # Eventos de automação
    DEVICE_CONNECTED = 'device_connected'
    DEVICE_DISCONNECTED = 'device_disconnected'
    AUTOMATION_TRIGGERED = 'automation_triggered'
    
    # Eventos de aprendizado
    USER_INTERACTION = 'user_interaction'
    PREFERENCE_LEARNED = 'preference_learned'
    PATTERN_DETECTED = 'pattern_detected'