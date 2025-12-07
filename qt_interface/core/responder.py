#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Voice Responder
Sistema de síntese de voz integrado
"""

import pyttsx3
import threading
from qt_interface.config import settings
from PyQt5.QtCore import QThread, pyqtSignal

class VoiceResponder(QThread):
    """Thread para síntese de voz"""
    
    # Sinais
    speech_started = pyqtSignal(str)
    speech_finished = pyqtSignal()
    speech_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.configure_voice()
        self.speech_queue = []
        self.is_speaking = False
        
    def configure_voice(self):
        """Configurar parâmetros de voz"""
        try:
            self.engine.setProperty('rate', settings.VOICE_RATE)
            self.engine.setProperty('volume', settings.VOICE_VOLUME)
            
            # Tentar definir voz em português
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'portuguese' in voice.name.lower() or 'brasil' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"Erro ao configurar voz: {e}")
    
    def speak_async(self, text):
        """Falar texto de forma assíncrona"""
        self.speech_queue.append(text)
        if not self.is_speaking:
            self.start()
    
    def speak_sync(self, text):
        """Falar texto de forma síncrona"""
        try:
            self.speech_started.emit(text)
            self.engine.say(text)
            self.engine.runAndWait()
            self.speech_finished.emit()
        except Exception as e:
            self.speech_error.emit(f"Erro na síntese de voz: {e}")
    
    def run(self):
        """Processar fila de fala"""
        self.is_speaking = True
        
        while self.speech_queue:
            text = self.speech_queue.pop(0)
            self.speak_sync(text)
        
        self.is_speaking = False

def speak(text):
    """Função simples para compatibilidade"""
    engine = pyttsx3.init()
    engine.setProperty('rate', settings.VOICE_RATE)
    engine.setProperty('volume', settings.VOICE_VOLUME)
    engine.say(text)
    engine.runAndWait()