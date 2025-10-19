#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Síntese de Voz do JARVIS
Converte texto para fala com personalidade elegante e profissional
"""

import pyttsx3
import threading
import time
import queue
import logging
from core.logger import JarvisLogger

class VoiceSynthesizer:
    """Sistema de síntese de voz com personalidade personalizada"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        
        # Configurações de voz
        voice_config = config.get('audio', {}).get('voice_settings', {})
        self.rate = voice_config.get('rate', 180)
        self.volume = voice_config.get('volume', 0.8)
        self.voice_id = voice_config.get('voice', 0)
        
        # Personalidade
        personality = config.get('jarvis', {}).get('personality', {})
        self.name = personality.get('name', 'JARVIS')
        self.tone = personality.get('tone', 'professional')
        self.style = personality.get('style', 'elegant')
        
        # Estados
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        
        # Inicializar engine
        self.engine = None
        self._initialize_engine()
        self._start_speech_thread()
    
    def _initialize_engine(self):
        """Inicializa o engine de síntese de voz"""
        try:
            self.engine = pyttsx3.init()
            
            # Configurar propriedades
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)
            
            # Configurar voz
            voices = self.engine.getProperty('voices')
            if voices and len(voices) > self.voice_id:
                self.engine.setProperty('voice', voices[self.voice_id].id)
                self.logger.voice(f"Voz configurada: {voices[self.voice_id].name}")
            
            self.logger.voice("Engine de síntese inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar engine de voz: {e}")
            raise
    
    def _start_speech_thread(self):
        """Inicia thread para processamento de fala"""
        self.speech_thread = threading.Thread(target=self._speech_worker)
        self.speech_thread.daemon = True
        self.speech_thread.start()
    
    def _speech_worker(self):
        """Worker thread para processar fila de fala"""
        while True:
            try:
                text, priority = self.speech_queue.get(timeout=1)
                if text is None:  # Sinal para parar
                    break
                
                self._speak_now(text)
                self.speech_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Erro no worker de fala: {e}")
    
    def _speak_now(self, text):
        """Executa a síntese de voz imediatamente"""
        try:
            self.is_speaking = True
            self.logger.voice(f"Falando: '{text}'")
            
            self.engine.say(text)
            self.engine.runAndWait()
            
        except Exception as e:
            self.logger.error(f"Erro na síntese de voz: {e}")
        finally:
            self.is_speaking = False
    
    def speak(self, text, priority=1):
        """Adiciona texto à fila de fala"""
        if not text or not text.strip():
            return
        
        # Processar texto com personalidade
        processed_text = self._apply_personality(text)
        
        # Adicionar à fila
        self.speech_queue.put((processed_text, priority))
    
    def speak_immediately(self, text):
        """Fala imediatamente, interrompendo outras falas"""
        if not text or not text.strip():
            return
        
        # Limpar fila
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        # Parar fala atual se houver
        if self.is_speaking and self.engine:
            self.engine.stop()
        
        # Processar e falar
        processed_text = self._apply_personality(text)
        self._speak_now(processed_text)
    
    def _apply_personality(self, text):
        """Aplica personalidade ao texto"""
        # Personalidade elegante e profissional
        if self.tone == 'professional' and self.style == 'elegant':
            # Adicionar saudações elegantes baseadas no horário
            current_hour = time.localtime().tm_hour
            
            # Substituir saudações genéricas
            if text.lower().startswith('olá') or text.lower().startswith('oi'):
                if 5 <= current_hour < 12:
                    greeting = "Bom dia"
                elif 12 <= current_hour < 18:
                    greeting = "Boa tarde"
                else:
                    greeting = "Boa noite"
                
                text = text[text.find(' ')+1:] if ' ' in text else ""
                text = f"{greeting}. {text}" if text else greeting
            
            # Adicionar formalidade
            text = text.replace("ok", "muito bem")
            text = text.replace("tá bom", "perfeito")
            text = text.replace("beleza", "excelente")
        
        return text
    
    def get_greeting(self):
        """Retorna saudação personalizada baseada no horário"""
        current_hour = time.localtime().tm_hour
        
        if 5 <= current_hour < 12:
            return "Bom dia. Como posso ajudá-lo hoje?"
        elif 12 <= current_hour < 18:
            return "Boa tarde. No que posso ser útil?"
        elif 18 <= current_hour < 22:
            return "Boa noite. Em que posso assistí-lo?"
        else:
            return "Olá. Como posso ajudá-lo neste momento?"
    
    def get_farewell(self):
        """Retorna despedida personalizada"""
        farewells = [
            "Foi um prazer ajudá-lo.",
            "Até a próxima. Estarei aqui quando precisar.",
            "Tenha um excelente dia.",
            "À sua disposição sempre."
        ]
        return farewells[hash(str(time.time())) % len(farewells)]
    
    def speak_startup(self):
        """Mensagem de inicialização do JARVIS"""
        startup_messages = [
            "JARVIS inicializado e operacional. Todos os sistemas funcionando normalmente.",
            "Olá. JARVIS está online e pronto para atendê-lo.",
            "Sistemas carregados com sucesso. JARVIS à sua disposição.",
            "Boa tarde. Sou JARVIS, seu assistente pessoal. Como posso ajudá-lo?"
        ]
        
        message = startup_messages[hash(str(time.time())) % len(startup_messages)]
        self.speak_immediately(message)
    
    def speak_error(self, error_type="general"):
        """Mensagens de erro personalizadas"""
        error_messages = {
            "general": "Desculpe, encontrei um problema técnico.",
            "connection": "Parece que há um problema de conexão.",
            "recognition": "Não consegui compreender claramente. Poderia repetir?",
            "service": "O serviço solicitado não está disponível no momento.",
            "permission": "Não tenho permissão para executar essa ação."
        }
        
        message = error_messages.get(error_type, error_messages["general"])
        self.speak_immediately(message)
    
    def stop_speaking(self):
        """Para toda síntese de voz"""
        # Limpar fila
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        # Parar engine
        if self.engine and self.is_speaking:
            self.engine.stop()
        
        self.logger.voice("Síntese de voz interrompida")
    
    def set_voice_rate(self, rate):
        """Ajusta velocidade da fala"""
        self.rate = max(50, min(300, rate))  # Limitar entre 50-300
        if self.engine:
            self.engine.setProperty('rate', self.rate)
        self.logger.voice(f"Velocidade da fala ajustada para: {self.rate}")
    
    def set_voice_volume(self, volume):
        """Ajusta volume da fala"""
        self.volume = max(0.0, min(1.0, volume))  # Limitar entre 0-1
        if self.engine:
            self.engine.setProperty('volume', self.volume)
        self.logger.voice(f"Volume ajustado para: {self.volume}")
    
    def list_available_voices(self):
        """Lista vozes disponíveis no sistema"""
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        voice_list = []
        
        for i, voice in enumerate(voices):
            voice_info = {
                'id': i,
                'name': voice.name,
                'languages': voice.languages,
                'gender': getattr(voice, 'gender', 'unknown')
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def change_voice(self, voice_index):
        """Muda a voz utilizada"""
        voices = self.engine.getProperty('voices')
        if voices and 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            self.voice_id = voice_index
            self.logger.voice(f"Voz alterada para: {voices[voice_index].name}")
            return True
        return False
    
    def shutdown(self):
        """Finaliza o sistema de síntese"""
        self.speech_queue.put((None, 0))  # Sinal para parar worker
        if self.speech_thread:
            self.speech_thread.join(timeout=2)
        
        if self.engine:
            self.engine.stop()
        
        self.logger.voice("Sistema de síntese finalizado")