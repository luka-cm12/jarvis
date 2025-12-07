#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Chatbot
Integração com IA avançada e OpenAI
"""

import sys
import os
from pathlib import Path

# Adicionar diretório pai para importações
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from src.ai.advanced_brain import AdvancedAI
    from qt_interface.config import settings
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    print("IA avançada não disponível, usando OpenAI diretamente")
    ADVANCED_AI_AVAILABLE = False

# Fallback para OpenAI direto se necessário
try:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
    OPENAI_AVAILABLE = True
except ImportError:
    print("OpenAI não disponível")
    OPENAI_AVAILABLE = False

class ChatBot:
    """Sistema de chat integrado com IA avançada"""
    
    def __init__(self):
        self.ai_brain = None
        self.conversation_history = []
        
        if ADVANCED_AI_AVAILABLE:
            try:
                self.ai_brain = AdvancedAI()
                print("✅ IA avançada carregada")
            except Exception as e:
                print(f"⚠️ Erro ao carregar IA avançada: {e}")
                self.ai_brain = None
    
    def get_response(self, prompt, context=None):
        """Obter resposta da IA"""
        try:
            # Usar IA avançada se disponível
            if self.ai_brain:
                response_data = self.ai_brain.process_input(prompt)
                response = response_data.get('response', 'Desculpe, não consegui processar isso.')
                
                # Adicionar ao histórico
                self.conversation_history.append({
                    'user': prompt,
                    'assistant': response,
                    'emotion': response_data.get('emotion', 'neutral'),
                    'confidence': response_data.get('confidence', 0.5)
                })
                
                return response
            
            # Fallback para OpenAI direto
            elif OPENAI_AVAILABLE:
                return self.get_openai_response(prompt)
            
            else:
                return "Desculpe, sistema de IA não está disponível no momento."
                
        except Exception as e:
            print(f"Erro no chatbot: {e}")
            return "Ocorreu um erro ao processar sua solicitação."
    
    def get_openai_response(self, prompt):
        """Resposta direta do OpenAI"""
        try:
            # Construir contexto com histórico
            messages = [
                {"role": "system", "content": "Você é JARVIS, um assistente inteligente inspirado no Homem de Ferro. Seja útil, inteligente e um pouco tecnológico."}
            ]
            
            # Adicionar histórico recente
            for item in self.conversation_history[-5:]:
                messages.append({"role": "user", "content": item['user']})
                messages.append({"role": "assistant", "content": item['assistant']})
            
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Adicionar ao histórico
            self.conversation_history.append({
                'user': prompt,
                'assistant': answer,
                'emotion': 'neutral',
                'confidence': 0.8
            })
            
            return answer
            
        except Exception as e:
            print(f'Erro OpenAI: {e}')
            return 'Desculpe, ocorreu um erro ao obter resposta da IA.'
    
    def get_conversation_summary(self):
        """Obter resumo da conversa"""
        if not self.conversation_history:
            return "Nenhuma conversa ainda."
        
        total = len(self.conversation_history)
        emotions = [item.get('emotion', 'neutral') for item in self.conversation_history]
        most_common_emotion = max(set(emotions), key=emotions.count)
        
        return {
            'total_exchanges': total,
            'dominant_emotion': most_common_emotion,
            'last_exchange': self.conversation_history[-1] if self.conversation_history else None
        }

# Função para compatibilidade
def get_response(prompt):
    """Função simples para compatibilidade"""
    bot = ChatBot()
    return bot.get_response(prompt)