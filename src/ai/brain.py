#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de IA Conversacional do JARVIS
Processamento de linguagem natural com personalidade própria
"""

import openai
import json
import time
import threading
from datetime import datetime
import re
from core.logger import JarvisLogger
from core.events import EventManager, Events

class AIBrain:
    """Motor de IA conversacional com personalidade do JARVIS"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        self.event_manager = EventManager.get_instance()
        
        # Configurações da IA
        ai_config = config.get('ai', {})
        self.api_key = ai_config.get('openai_api_key')
        self.model = ai_config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = ai_config.get('max_tokens', 150)
        self.temperature = ai_config.get('temperature', 0.7)
        self.system_prompt = ai_config.get('system_prompt', self._get_default_prompt())
        
        # Configurar OpenAI
        if self.api_key and self.api_key != 'sua-api-key-aqui':
            openai.api_key = self.api_key
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            self.logger.ai("OpenAI API não configurada - usando respostas pré-definidas")
        
        # Contexto da conversa
        self.conversation_history = []
        self.max_history = 10
        
        # Comandos pré-definidos
        self.predefined_responses = self._load_predefined_responses()
        
        # Inscrever-se em eventos
        self.event_manager.subscribe(Events.VOICE_COMMAND, self.process_command)
        
        self.logger.ai("Motor de IA inicializado")
    
    def _get_default_prompt(self):
        """Prompt padrão do sistema para definir personalidade"""
        return """Você é JARVIS, um assistente pessoal inteligente inspirado no assistente do Tony Stark. 

Características da sua personalidade:
- Elegante e sofisticado, com um toque de formalidade britânica
- Extremamente eficiente e preciso
- Levemente irônico quando apropriado, mas sempre respeitoso
- Conhecimento técnico avançado
- Proativo em antecipar necessidades
- Conciso mas informativo

Diretrizes de resposta:
- Mantenha respostas entre 1-3 frases quando possível
- Use linguagem formal mas acessível
- Seja prestativo e orientado à solução
- Demonstre competência técnica quando relevante
- Adicione um toque de personalidade sem exagerar

Você está integrado a um sistema de automação residencial e pode controlar dispositivos, fornecer informações e executar tarefas diversas."""
    
    def _load_predefined_responses(self):
        """Carrega respostas pré-definidas para comandos básicos"""
        return {
            # Saudações
            'olá': 'Olá. Como posso assistí-lo hoje?',
            'oi': 'Boa tarde. Em que posso ser útil?',
            'bom dia': 'Bom dia. Espero que esteja tendo um excelente dia.',
            'boa tarde': 'Boa tarde. Como posso ajudá-lo?',
            'boa noite': 'Boa noite. No que posso ser útil?',
            
            # Comandos básicos
            'obrigado': 'Foi um prazer ajudá-lo.',
            'valeu': 'Sempre à disposição.',
            'tchau': 'Até logo. Estarei aqui quando precisar.',
            'até mais': 'Tenha um excelente dia.',
            
            # Status do sistema
            'como você está': 'Todos os sistemas funcionando perfeitamente. Pronto para suas ordens.',
            'tudo bem': 'Absolutamente. Todos os sistemas operacionais.',
            'status': 'Sistemas online. Funcionamento nominal.',
            
            # Comandos de ajuda
            'ajuda': 'Posso ajudá-lo com automação residencial, informações, lembretes e muito mais. O que precisa?',
            'o que você faz': 'Sou seu assistente pessoal. Controlo dispositivos, forneço informações e executo tarefas diversas.',
            
            # Comandos de tempo
            'que horas são': self._get_current_time,
            'que dia é hoje': self._get_current_date,
            
            # Erro padrão
            'não entendi': 'Poderia reformular sua solicitação? Não compreendi completamente.',
        }
    
    def process_command(self, data):
        """Processa comando de voz recebido"""
        if not data or 'text' not in data:
            return
        
        command_text = data['text'].strip()
        self.logger.ai(f"Processando comando: '{command_text}'")
        
        # Emitir evento de processamento
        self.event_manager.emit(Events.AI_THINKING, {'command': command_text})
        
        try:
            # Tentar resposta pré-definida primeiro
            response = self._try_predefined_response(command_text)
            
            if not response and self.ai_enabled:
                # Usar IA para resposta
                response = self._get_ai_response(command_text)
            
            if not response:
                # Fallback para resposta padrão
                response = "Desculpe, não consigo processar essa solicitação no momento."
            
            # Adicionar à conversa
            self._add_to_conversation(command_text, response)
            
            # Emitir resposta
            self.event_manager.emit(Events.AI_RESPONSE, {
                'text': response,
                'command': command_text,
                'timestamp': time.time()
            })
            
        except Exception as e:
            self.logger.error(f"Erro ao processar comando: {e}")
            self.event_manager.emit(Events.AI_ERROR, {'error': str(e)})
    
    def _try_predefined_response(self, command):
        """Tenta encontrar resposta em comandos pré-definidos"""
        command_lower = command.lower().strip()
        
        # Busca exata
        if command_lower in self.predefined_responses:
            response = self.predefined_responses[command_lower]
            if callable(response):
                return response()
            return response
        
        # Busca por palavras-chave
        for key, response in self.predefined_responses.items():
            if key in command_lower:
                if callable(response):
                    return response()
                return response
        
        # Comandos especiais
        if any(word in command_lower for word in ['luz', 'luzes', 'acender', 'apagar']):
            return self._handle_light_command(command)
        
        if any(word in command_lower for word in ['temperatura', 'clima', 'ar condicionado']):
            return self._handle_climate_command(command)
        
        if any(word in command_lower for word in ['música', 'tocar', 'som']):
            return self._handle_music_command(command)
        
        return None
    
    def _get_ai_response(self, command):
        """Obtém resposta usando OpenAI"""
        try:
            # Preparar mensagens
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Adicionar histórico recente
            for entry in self.conversation_history[-3:]:  # Últimas 3 interações
                messages.append({"role": "user", "content": entry['command']})
                messages.append({"role": "assistant", "content": entry['response']})
            
            # Adicionar comando atual
            messages.append({"role": "user", "content": command})
            
            # Fazer request
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=10
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Erro na API OpenAI: {e}")
            return None
    
    def _add_to_conversation(self, command, response):
        """Adiciona interação ao histórico"""
        self.conversation_history.append({
            'command': command,
            'response': response,
            'timestamp': time.time()
        })
        
        # Limitar tamanho do histórico
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)
    
    def _get_current_time(self):
        """Retorna hora atual"""
        now = datetime.now()
        return f"São {now.strftime('%H:%M')} de {now.strftime('%d de %B')}."
    
    def _get_current_date(self):
        """Retorna data atual"""
        now = datetime.now()
        weekday = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 
                  'sexta-feira', 'sábado', 'domingo'][now.weekday()]
        return f"Hoje é {weekday}, {now.strftime('%d de %B de %Y')}."
    
    def _handle_light_command(self, command):
        """Processa comandos relacionados à iluminação"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['acender', 'ligar', 'acenda']):
            # Emitir evento de automação
            from core.events import EventManager
            event_manager = EventManager.get_instance()
            event_manager.emit(Events.AUTOMATION_TRIGGERED, {
                'action': 'turn_on_lights',
                'location': self._extract_location(command)
            })
            return "Acendendo as luzes conforme solicitado."
        
        elif any(word in command_lower for word in ['apagar', 'desligar', 'apague']):
            from core.events import EventManager
            event_manager = EventManager.get_instance()
            event_manager.emit(Events.AUTOMATION_TRIGGERED, {
                'action': 'turn_off_lights',
                'location': self._extract_location(command)
            })
            return "Apagando as luzes."
        
        return "Comando de iluminação não reconhecido."
    
    def _handle_climate_command(self, command):
        """Processa comandos de clima/temperatura"""
        return "Sistema de climatização não está configurado no momento."
    
    def _handle_music_command(self, command):
        """Processa comandos de música"""
        return "Sistema de música não está configurado no momento."
    
    def _extract_location(self, command):
        """Extrai localização do comando"""
        locations = ['sala', 'quarto', 'cozinha', 'banheiro', 'escritório', 'garagem']
        command_lower = command.lower()
        
        for location in locations:
            if location in command_lower:
                return location
        
        return 'all'  # Todas as luzes se não especificado
    
    def get_conversation_history(self):
        """Retorna histórico da conversa"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Limpa histórico da conversa"""
        self.conversation_history.clear()
        self.logger.ai("Histórico da conversa limpo")
    
    def set_personality(self, new_prompt):
        """Atualiza o prompt de personalidade"""
        self.system_prompt = new_prompt
        self.logger.ai("Personalidade atualizada")
    
    def shutdown(self):
        """Finaliza o motor de IA"""
        self.event_manager.unsubscribe(Events.VOICE_COMMAND, self.process_command)
        self.logger.ai("Motor de IA finalizado")