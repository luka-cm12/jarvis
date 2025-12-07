#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Advanced AI Brain
Sistema de IA avançado com aprendizado e personalidade
"""

import json
import sqlite3
import openai
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from textblob import TextBlob
import pickle
import os

class AdvancedAI:
    """Sistema de IA avançado do JARVIS"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.personality = {
            'humor_level': 0.7,
            'sarcasm_level': 0.3,
            'formality_level': 0.6,
            'helpfulness': 0.9,
            'curiosity': 0.8
        }
        
        self.knowledge_base = {}
        self.user_preferences = {}
        self.conversation_history = []
        self.learning_patterns = defaultdict(int)
        self.db_path = "data/ai_memory.sqlite"
        
        self.init_database()
        self.load_personality()
        self.load_knowledge()
    
    def init_database(self):
        """Inicializar banco de dados de memória"""
        os.makedirs("data", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de conversas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                user_input TEXT,
                ai_response TEXT,
                context TEXT,
                emotion_detected TEXT,
                learning_tags TEXT
            )
        ''')
        
        # Tabela de preferências do usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                category TEXT,
                preference_key TEXT,
                preference_value TEXT,
                confidence REAL,
                last_updated DATETIME,
                PRIMARY KEY (category, preference_key)
            )
        ''')
        
        # Tabela de conhecimento aprendido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                topic TEXT PRIMARY KEY,
                knowledge_data TEXT,
                source TEXT,
                confidence REAL,
                created_at DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_emotion(self, text):
        """Análise de emoção no texto"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        elif abs(polarity) < 0.1:
            return "neutral"
        else:
            return "mixed"
    
    def detect_intent(self, text):
        """Detectar intenção do usuário"""
        text_lower = text.lower()
        
        # Palavras-chave para diferentes intenções
        intents = {
            'question': ['o que', 'como', 'quando', 'onde', 'por que', 'quem', '?'],
            'command': ['faça', 'execute', 'rode', 'inicie', 'pare', 'abra', 'feche'],
            'learning': ['aprenda', 'lembre', 'salve', 'memorize', 'guarde'],
            'personal': ['prefiro', 'gosto', 'odeio', 'amo', 'não gosto'],
            'network': ['rede', 'scan', 'dispositivos', 'ip', 'hack', 'vulnerabilidades'],
            'system': ['status', 'sistema', 'módulos', 'funcionando', 'online'],
            'casual': ['oi', 'olá', 'tchau', 'obrigado', 'valeu']
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents[0] if detected_intents else 'general'
    
    def learn_from_interaction(self, user_input, context=None):
        """Aprender com a interação do usuário"""
        emotion = self.analyze_emotion(user_input)
        intent = self.detect_intent(user_input)
        
        # Extrair padrões de preferência
        if intent == 'personal':
            self.extract_preferences(user_input)
        
        # Atualizar padrões de aprendizado
        self.learning_patterns[f"intent_{intent}"] += 1
        self.learning_patterns[f"emotion_{emotion}"] += 1
        
        # Salvar na memória
        self.save_conversation(user_input, "", context, emotion, [intent])
        
        return {
            'emotion': emotion,
            'intent': intent,
            'learned': True
        }
    
    def extract_preferences(self, text):
        """Extrair preferências do texto"""
        text_lower = text.lower()
        
        # Padrões de preferência
        preferences = {}
        
        # Gostos e desgostos
        if 'gosto de' in text_lower or 'amo' in text_lower:
            # Extrair o que o usuário gosta
            parts = text_lower.split('gosto de')
            if len(parts) > 1:
                preference = parts[1].strip()
                preferences['likes'] = preference
        
        if 'não gosto' in text_lower or 'odeio' in text_lower:
            # Extrair o que o usuário não gosta
            parts = text_lower.split('não gosto de') or text_lower.split('odeio')
            if len(parts) > 1:
                preference = parts[1].strip()
                preferences['dislikes'] = preference
        
        # Salvar preferências
        for category, value in preferences.items():
            self.save_preference('general', category, value, 0.8)
    
    def generate_response(self, user_input, context=None):
        """Gerar resposta inteligente"""
        # Analisar entrada
        analysis = self.learn_from_interaction(user_input, context)
        intent = analysis['intent']
        emotion = analysis['emotion']
        
        # Buscar na base de conhecimento
        relevant_knowledge = self.search_knowledge(user_input)
        
        # Gerar resposta baseada na intenção
        if intent == 'question':
            response = self.answer_question(user_input, relevant_knowledge)
        elif intent == 'command':
            response = self.handle_command(user_input)
        elif intent == 'network':
            response = self.handle_network_query(user_input)
        elif intent == 'learning':
            response = self.handle_learning_request(user_input)
        elif intent == 'casual':
            response = self.casual_response(user_input, emotion)
        else:
            response = self.general_response(user_input, relevant_knowledge)
        
        # Personalizar resposta baseada na personalidade
        response = self.add_personality(response, emotion)
        
        # Salvar conversa completa
        self.save_conversation(user_input, response, context, emotion, [intent])
        
        return response
    
    def answer_question(self, question, knowledge):
        """Responder perguntas usando conhecimento"""
        if knowledge:
            return f"Com base no que sei: {knowledge[0]['data'][:200]}..."
        
        # Respostas padrão para perguntas comuns
        question_lower = question.lower()
        
        if 'como você funciona' in question_lower:
            return "Sou um sistema de IA avançado com capacidades de aprendizado, análise de rede e automação. Posso aprender com nossas conversas e me adaptar às suas preferências."
        
        if 'o que você sabe' in question_lower:
            return f"Tenho conhecimento sobre {len(self.knowledge_base)} tópicos diferentes e {len(self.conversation_history)} conversas anteriores registradas."
        
        return "Interessante pergunta. Deixe-me pensar... Posso pesquisar mais sobre isso se desejar."
    
    def handle_command(self, command):
        """Lidar com comandos"""
        command_lower = command.lower()
        
        if 'scan' in command_lower or 'rede' in command_lower:
            return "Iniciando varredura de rede... Isso pode levar alguns minutos. Vou te notificar quando encontrar algo interessante."
        
        if 'aprenda' in command_lower:
            return "Modo de aprendizado ativado. Me conte o que você gostaria que eu soubesse."
        
        return "Comando recebido. Executando..."
    
    def handle_network_query(self, query):
        """Lidar com consultas de rede"""
        return "Acessando sistemas de rede... Analisando dispositivos conectados e identificando vulnerabilidades. Momento."
    
    def casual_response(self, input_text, emotion):
        """Resposta casual baseada na emoção"""
        responses = {
            'positive': [
                "Que bom te ver animado!",
                "Energia positiva detectada! Como posso ajudar?",
                "Excelente! Vamos trabalhar juntos."
            ],
            'negative': [
                "Percebi que algo não está bem. Posso ajudar de alguma forma?",
                "Vamos resolver isso juntos.",
                "Estou aqui para apoiar você."
            ],
            'neutral': [
                "Olá! Pronto para mais um dia produtivo?",
                "Oi! Em que posso ser útil hoje?",
                "Presente e operacional. Como posso ajudar?"
            ]
        }
        
        return random.choice(responses.get(emotion, responses['neutral']))
    
    def add_personality(self, response, emotion):
        """Adicionar personalidade à resposta"""
        # Adicionar humor se apropriado
        if self.personality['humor_level'] > 0.5 and emotion == 'positive':
            humor_additions = [
                " 😊",
                " (com um sorriso digital)",
                " - sempre bom manter o astral!",
                " ✨"
            ]
            if random.random() < 0.3:
                response += random.choice(humor_additions)
        
        # Adicionar formalidade
        if self.personality['formality_level'] > 0.7:
            if not response.endswith('.'):
                response += '.'
            response = response.replace('você', 'senhor(a)')
        
        return response
    
    def save_conversation(self, user_input, ai_response, context, emotion, learning_tags):
        """Salvar conversa no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, user_input, ai_response, context, emotion_detected, learning_tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            user_input,
            ai_response,
            json.dumps(context) if context else None,
            emotion,
            json.dumps(learning_tags)
        ))
        
        conn.commit()
        conn.close()
    
    def save_preference(self, category, key, value, confidence):
        """Salvar preferência do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (category, preference_key, preference_value, confidence, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, key, value, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def search_knowledge(self, query):
        """Buscar conhecimento relevante"""
        # Implementação básica - pode ser melhorada com embeddings
        query_words = query.lower().split()
        relevant = []
        
        for topic, data in self.knowledge_base.items():
            if any(word in topic.lower() for word in query_words):
                relevant.append({'topic': topic, 'data': data})
        
        return relevant[:3]  # Retornar top 3
    
    def load_personality(self):
        """Carregar personalidade salva"""
        try:
            with open("data/personality.json", "r") as f:
                saved_personality = json.load(f)
                self.personality.update(saved_personality)
        except FileNotFoundError:
            # Salvar personalidade padrão
            self.save_personality()
    
    def save_personality(self):
        """Salvar personalidade"""
        os.makedirs("data", exist_ok=True)
        with open("data/personality.json", "w") as f:
            json.dump(self.personality, f, indent=2)
    
    def load_knowledge(self):
        """Carregar base de conhecimento"""
        try:
            with open("data/knowledge_base.pkl", "rb") as f:
                self.knowledge_base = pickle.load(f)
        except FileNotFoundError:
            self.knowledge_base = {}
    
    def save_knowledge(self):
        """Salvar base de conhecimento"""
        os.makedirs("data", exist_ok=True)
        with open("data/knowledge_base.pkl", "wb") as f:
            pickle.dump(self.knowledge_base, f)
    
    def get_learning_stats(self):
        """Obter estatísticas de aprendizado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de conversas
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Preferências aprendidas
        cursor.execute('SELECT COUNT(*) FROM user_preferences')
        total_preferences = cursor.fetchone()[0]
        
        # Conhecimento acumulado
        cursor.execute('SELECT COUNT(*) FROM knowledge_base')
        total_knowledge = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'conversations': total_conversations,
            'preferences': total_preferences,
            'knowledge_items': total_knowledge,
            'learning_patterns': dict(self.learning_patterns),
            'personality': self.personality
        }

# Classe para processamento de linguagem natural avançado
class NLPProcessor:
    """Processador de linguagem natural avançado"""
    
    def __init__(self):
        self.entity_patterns = {
            'time': r'\b\d{1,2}:\d{2}\b',
            'date': r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
            'ip': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
    
    def extract_entities(self, text):
        """Extrair entidades do texto"""
        import re
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def sentiment_analysis_advanced(self, text):
        """Análise de sentimento avançada"""
        blob = TextBlob(text)
        
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity,
            'emotion': self.map_emotion(blob.sentiment.polarity, blob.sentiment.subjectivity)
        }
    
    def map_emotion(self, polarity, subjectivity):
        """Mapear polaridade para emoção específica"""
        if polarity > 0.5:
            return "joy" if subjectivity > 0.5 else "satisfaction"
        elif polarity > 0:
            return "contentment" if subjectivity > 0.5 else "approval"
        elif polarity > -0.5:
            return "disappointment" if subjectivity > 0.5 else "dissatisfaction"
        else:
            return "anger" if subjectivity > 0.5 else "frustration"

if __name__ == "__main__":
    # Teste do sistema de IA
    ai = AdvancedAI()
    
    print("🤖 JARVIS AI System Test")
    print("=" * 30)
    
    test_inputs = [
        "Olá JARVIS, como você está?",
        "Faça um scan da rede para encontrar vulnerabilidades",
        "Eu gosto muito de tecnologia e programação",
        "O que você sabe sobre segurança de redes?",
        "Aprenda que minha cor favorita é azul"
    ]
    
    for input_text in test_inputs:
        print(f"\n👤 User: {input_text}")
        response = ai.generate_response(input_text)
        print(f"🤖 JARVIS: {response}")
    
    # Mostrar estatísticas
    stats = ai.get_learning_stats()
    print(f"\n📊 Learning Stats: {stats}")