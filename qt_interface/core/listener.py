#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Voice Listener
Sistema de reconhecimento de voz integrado
"""

import speech_recognition as sr
import threading
import time
from qt_interface.config import settings
from PyQt5.QtCore import QThread, pyqtSignal

class VoiceListener(QThread):
    """Thread para reconhecimento de voz"""
    
    # Sinais
    command_recognized = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.should_stop = False
        
        # Calibrar ruído ambiente
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            print(f"Erro ao calibrar microfone: {e}")
    
    def start_listening(self):
        """Iniciar escuta contínua"""
        if not self.is_listening:
            self.should_stop = False
            self.start()
    
    def stop_listening(self):
        """Parar escuta"""
        self.should_stop = True
        self.is_listening = False
        self.listening_stopped.emit()
    
    def listen_once(self):
        """Escutar um comando único"""
        try:
            with self.microphone as source:
                self.listening_started.emit()
                audio = self.recognizer.listen(source, timeout=settings.LISTEN_TIMEOUT)
                text = self.recognizer.recognize_google(audio, language=settings.LANGUAGE)
                self.command_recognized.emit(text)
                return text
        except sr.WaitTimeoutError:
            self.error_occurred.emit("Timeout: Nenhum comando detectado")
            return None
        except sr.UnknownValueError:
            self.error_occurred.emit("Não foi possível entender o áudio")
            return None
        except sr.RequestError as e:
            self.error_occurred.emit(f"Erro no serviço de reconhecimento: {e}")
            return None
        except Exception as e:
            self.error_occurred.emit(f"Erro inesperado: {e}")
            return None
        finally:
            self.listening_stopped.emit()
    
    def run(self):
        """Loop principal da thread"""
        self.is_listening = True
        
        while not self.should_stop:
            try:
                command = self.listen_once()
                if command:
                    self.command_recognized.emit(command)
                time.sleep(0.1)  # Pequena pausa
            except Exception as e:
                self.error_occurred.emit(f"Erro no loop de escuta: {e}")
                break
        
        self.is_listening = False

def listen_command(timeout=settings.LISTEN_TIMEOUT):
    """Função simples para compatibilidade"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print('Ouvindo...')
        try:
            audio = recognizer.listen(source, timeout=timeout)
            text = recognizer.recognize_google(audio, language=settings.LANGUAGE)
            return text
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f'Erro ao reconhecer: {e}')
            return None