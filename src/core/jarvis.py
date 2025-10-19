#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Núcleo Principal do JARVIS
Integra todos os sistemas e gerencia o funcionamento geral
"""

import asyncio
import signal
import sys
import time
from datetime import datetime
import threading

from core.logger import JarvisLogger
from core.events import EventManager, Events
from core.voice_recognition import VoiceRecognizer
from core.voice_synthesis import VoiceSynthesizer
from ai.brain import AIBrain

class JARVIS:
    """Classe principal do assistente JARVIS"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        self.event_manager = EventManager.get_instance()
        
        # Estados do sistema
        self.is_running = False
        self.is_initialized = False
        
        # Componentes principais
        self.voice_recognizer = None
        self.voice_synthesizer = None
        self.ai_brain = None
        
        # Configurar handlers de sinal
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Inscrever-se em eventos
        self._setup_event_handlers()
        
        self.logger.system("JARVIS criado")
    
    def _setup_event_handlers(self):
        """Configura handlers para eventos do sistema"""
        self.event_manager.subscribe(Events.WAKE_WORD_DETECTED, self._on_wake_word)
        self.event_manager.subscribe(Events.AI_RESPONSE, self._on_ai_response)
        self.event_manager.subscribe(Events.SYSTEM_ERROR, self._on_system_error)
        self.event_manager.subscribe(Events.AUTOMATION_TRIGGERED, self._on_automation_triggered)
    
    async def initialize(self):
        """Inicializa todos os componentes do sistema"""
        try:
            self.logger.system("Inicializando componentes do JARVIS...")
            
            # Inicializar síntese de voz primeiro
            self.logger.system("🔊 Inicializando sistema de síntese de voz...")
            self.voice_synthesizer = VoiceSynthesizer(self.config)
            
            # Inicializar reconhecimento de voz
            self.logger.system("🎤 Inicializando sistema de reconhecimento de voz...")
            self.voice_recognizer = VoiceRecognizer(self.config)
            
            # Inicializar motor de IA
            self.logger.system("🧠 Inicializando motor de IA...")
            self.ai_brain = AIBrain(self.config)
            
            # Testar componentes
            await self._run_system_tests()
            
            self.is_initialized = True
            self.logger.system("✅ Todos os componentes inicializados com sucesso")
            
            # Emitir evento de startup
            self.event_manager.emit(Events.SYSTEM_STARTUP, {
                'timestamp': time.time(),
                'version': '1.0.0'
            })
            
        except Exception as e:
            self.logger.error(f"Erro na inicialização: {e}")
            await self.shutdown()
            raise
    
    async def _run_system_tests(self):
        """Executa testes básicos dos componentes"""
        self.logger.system("Executando testes do sistema...")
        
        # Teste de síntese de voz
        if self.voice_synthesizer:
            self.voice_synthesizer.speak_startup()
            await asyncio.sleep(2)  # Aguardar fala terminar
        
        # Teste de reconhecimento (opcional)
        test_microphone = self.config.get('jarvis', {}).get('test_on_startup', False)
        if test_microphone and self.voice_recognizer:
            self.logger.system("Testando microfone...")
            if self.voice_recognizer.test_microphone():
                self.logger.system("✅ Teste de microfone bem-sucedido")
            else:
                self.logger.system("⚠️ Teste de microfone falhou - continuando mesmo assim")
    
    async def run(self):
        """Loop principal de execução do JARVIS"""
        try:
            await self.initialize()
            
            if not self.is_initialized:
                self.logger.error("Falha na inicialização - abortando")
                return
            
            self.is_running = True
            self.logger.system("🟢 JARVIS está online e operacional!")
            
            # Iniciar escuta de voz
            if self.voice_recognizer:
                continuous_listening = self.config.get('features', {}).get('continuous_listening', True)
                if continuous_listening:
                    self.voice_recognizer.start_listening()
                    self.logger.voice("Modo de escuta contínua ativado")
            
            # Loop principal
            while self.is_running:
                await self._main_loop_iteration()
                await asyncio.sleep(0.1)  # Pequena pausa para não sobrecarregar
                
        except KeyboardInterrupt:
            self.logger.system("Interrupção pelo usuário detectada")
        except Exception as e:
            self.logger.error(f"Erro no loop principal: {e}")
        finally:
            await self.shutdown()
    
    async def _main_loop_iteration(self):
        """Uma iteração do loop principal"""
        # Verificar saúde dos componentes
        await self._health_check()
        
        # Processar tarefas agendadas
        await self._process_scheduled_tasks()
        
        # Verificar se precisa executar manutenção
        await self._maintenance_check()
    
    async def _health_check(self):
        """Verifica saúde dos componentes principais"""
        # Implementar verificações de saúde se necessário
        pass
    
    async def _process_scheduled_tasks(self):
        """Processa tarefas agendadas"""
        # Implementar sistema de tarefas agendadas
        pass
    
    async def _maintenance_check(self):
        """Executa verificações de manutenção periódica"""
        # Implementar manutenção automática
        pass
    
    def _on_wake_word(self, data):
        """Handler para detecção de wake word"""
        self.logger.voice("Wake word detectado - JARVIS ativado!")
        
        if self.voice_synthesizer:
            responses = [
                "Sim, senhor?",
                "Como posso ajudá-lo?",
                "Às suas ordens.",
                "Ouvindo."
            ]
            response = responses[hash(str(time.time())) % len(responses)]
            self.voice_synthesizer.speak(response)
    
    def _on_ai_response(self, data):
        """Handler para resposta da IA"""
        if not data or 'text' not in data:
            return
        
        response_text = data['text']
        self.logger.ai(f"Resposta gerada: '{response_text}'")
        
        # Falar resposta
        if self.voice_synthesizer:
            self.voice_synthesizer.speak(response_text)
        
        # Log da interação
        self.event_manager.emit(Events.USER_INTERACTION, {
            'command': data.get('command', ''),
            'response': response_text,
            'timestamp': time.time()
        })
    
    def _on_system_error(self, data):
        """Handler para erros do sistema"""
        error_msg = data.get('error', 'Erro desconhecido') if data else 'Erro desconhecido'
        self.logger.error(f"Erro do sistema: {error_msg}")
        
        if self.voice_synthesizer:
            self.voice_synthesizer.speak_error()
    
    def _on_automation_triggered(self, data):
        """Handler para eventos de automação"""
        if not data:
            return
        
        action = data.get('action', '')
        self.logger.automation(f"Automação disparada: {action}")
        
        # Aqui seria implementada a integração com sistemas de automação
        # Por enquanto, apenas simulamos a ação
        if action == 'turn_on_lights':
            location = data.get('location', 'all')
            self.logger.automation(f"Simulando: acender luzes em '{location}'")
        elif action == 'turn_off_lights':
            location = data.get('location', 'all')
            self.logger.automation(f"Simulando: apagar luzes em '{location}'")
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais do sistema (Ctrl+C, etc.)"""
        self.logger.system(f"Sinal recebido: {signum}")
        self.is_running = False
    
    async def shutdown(self):
        """Finaliza o JARVIS de forma limpa"""
        self.logger.system("Iniciando desligamento do JARVIS...")
        self.is_running = False
        
        # Emitir evento de shutdown
        self.event_manager.emit(Events.SYSTEM_SHUTDOWN, {
            'timestamp': time.time(),
            'reason': 'normal_shutdown'
        })
        
        # Mensagem de despedida
        if self.voice_synthesizer:
            farewell = self.voice_synthesizer.get_farewell()
            self.voice_synthesizer.speak_immediately(farewell)
            await asyncio.sleep(2)  # Aguardar fala terminar
        
        # Finalizar componentes
        if self.voice_recognizer:
            self.voice_recognizer.stop_listening()
        
        if self.ai_brain:
            self.ai_brain.shutdown()
        
        if self.voice_synthesizer:
            self.voice_synthesizer.shutdown()
        
        self.logger.system("🔴 JARVIS desligado com sucesso")
    
    def get_status(self):
        """Retorna status atual do sistema"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'components': {
                'voice_recognition': self.voice_recognizer is not None,
                'voice_synthesis': self.voice_synthesizer is not None,
                'ai_brain': self.ai_brain is not None
            },
            'uptime': time.time() - (self.start_time if hasattr(self, 'start_time') else time.time()),
            'version': '1.0.0'
        }
    
    def execute_command(self, command_text):
        """Executa um comando diretamente (útil para interface web)"""
        if not self.ai_brain:
            return "Sistema de IA não está disponível"
        
        # Simular evento de comando de voz
        self.event_manager.emit(Events.VOICE_COMMAND, {
            'text': command_text,
            'timestamp': time.time(),
            'source': 'direct'
        })
        
        return "Comando processado"