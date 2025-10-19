#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Reconhecimento de Voz do JARVIS
Processa entrada de áudio e converte para texto
"""

import speech_recognition as sr
import pyaudio
import threading
import time
from queue import Queue
import logging
from core.logger import JarvisLogger

class VoiceRecognizer:
    """Sistema de reconhecimento de voz com suporte a múltiplos engines"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        
        # Configurações de áudio
        self.sample_rate = config.get('audio', {}).get('sample_rate', 16000)
        self.chunk_size = config.get('audio', {}).get('chunk_size', 1024)
        self.channels = config.get('audio', {}).get('channels', 1)
        
        # Wake word e configurações
        self.wake_word = config.get('jarvis', {}).get('wake_word', 'jarvis').lower()
        self.language = config.get('jarvis', {}).get('personality', {}).get('language', 'pt-BR')
        
        # Estados
        self.is_listening = False
        self.is_activated = False
        self.listening_thread = None
        self.audio_queue = Queue()
        
        # Inicializar recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        self._initialize_microphone()
        self._calibrate_microphone()
    
    def _initialize_microphone(self):
        """Inicializa o microfone"""
        try:
            device_index = self.config.get('audio', {}).get('input_device')
            self.microphone = sr.Microphone(device_index=device_index)
            self.logger.voice("Microfone inicializado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar microfone: {e}")
            raise
    
    def _calibrate_microphone(self):
        """Calibra o microfone para ruído ambiente"""
        try:
            with self.microphone as source:
                self.logger.voice("Calibrando para ruído ambiente...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.voice("Calibração concluída")
        except Exception as e:
            self.logger.error(f"Erro na calibração do microfone: {e}")
    
    def start_listening(self):
        """Inicia o modo de escuta contínua"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listen_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
        self.logger.voice("Escuta iniciada - aguardando wake word...")
    
    def stop_listening(self):
        """Para o modo de escuta"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)
        self.logger.voice("Escuta interrompida")
    
    def _listen_loop(self):
        """Loop principal de escuta"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Escuta com timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                # Processar áudio em thread separada
                threading.Thread(target=self._process_audio, args=(audio,)).start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Erro no loop de escuta: {e}")
                time.sleep(1)
    
    def _process_audio(self, audio):
        """Processa o áudio capturado"""
        try:
            # Reconhecer fala usando Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            text_lower = text.lower()
            
            self.logger.voice(f"Texto reconhecido: '{text}'")
            
            # Verificar wake word
            if not self.is_activated and self.wake_word in text_lower:
                self.is_activated = True
                self.logger.voice("Wake word detectado - JARVIS ativado!")
                self._on_wake_word_detected(text)
                
            elif self.is_activated:
                # Processar comando
                self._on_command_received(text)
                self.is_activated = False  # Desativar após comando
                
        except sr.UnknownValueError:
            # Não conseguiu entender o áudio - normal, não logar
            pass
        except sr.RequestError as e:
            self.logger.error(f"Erro no serviço de reconhecimento: {e}")
        except Exception as e:
            self.logger.error(f"Erro no processamento de áudio: {e}")
    
    def _on_wake_word_detected(self, text):
        """Callback quando wake word é detectado"""
        # Implementar resposta de ativação
        from core.events import EventManager
        EventManager.emit('wake_word_detected', {'text': text})
    
    def _on_command_received(self, text):
        """Callback quando comando é recebido"""
        from core.events import EventManager
        EventManager.emit('voice_command', {'text': text, 'timestamp': time.time()})
    
    def listen_once(self, timeout=5):
        """Escuta uma única vez e retorna o texto"""
        try:
            with self.microphone as source:
                self.logger.voice("Escutando comando...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio, language=self.language)
            self.logger.voice(f"Comando recebido: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            self.logger.voice("Timeout - nenhum áudio detectado")
            return None
        except sr.UnknownValueError:
            self.logger.voice("Não foi possível entender o áudio")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao escutar: {e}")
            return None
    
    def test_microphone(self):
        """Testa o funcionamento do microfone"""
        try:
            self.logger.voice("Testando microfone... Diga algo!")
            text = self.listen_once(timeout=5)
            
            if text:
                self.logger.voice(f"Teste bem-sucedido! Você disse: '{text}'")
                return True
            else:
                self.logger.error("Teste falhou - nenhum áudio reconhecido")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro no teste do microfone: {e}")
            return False