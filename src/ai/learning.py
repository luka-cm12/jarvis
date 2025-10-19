#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Aprendizado Contínuo do JARVIS
Machine Learning para adaptação às preferências do usuário
"""

import sqlite3
import json
import pickle
import numpy as np
from datetime import datetime, timedelta
import threading
from collections import defaultdict, Counter
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import StandardScaler

from core.logger import JarvisLogger
from core.events import EventManager, Events

class LearningSystem:
    """Sistema de aprendizado contínuo para personalização"""
    
    def __init__(self, config):
        self.config = config
        self.logger = JarvisLogger(__name__)
        self.event_manager = EventManager.get_instance()
        
        # Configurações
        self.db_path = config.get('database', {}).get('path', 'data/jarvis.db')
        self.learning_enabled = config.get('features', {}).get('learning_mode', True)
        
        # Modelos ML
        self.command_classifier = None
        self.preference_model = None
        self.pattern_detector = None
        
        # Dados de aprendizado
        self.interaction_history = []
        self.user_preferences = {}
        self.command_patterns = defaultdict(list)
        self.usage_patterns = defaultdict(int)
        
        # Configurar banco de dados
        self._init_database()
        
        # Carregar dados existentes
        self._load_existing_data()
        
        # Configurar eventos
        self._setup_event_handlers()
        
        # Thread de aprendizado
        self.learning_thread = None
        self.learning_active = False
        
        if self.learning_enabled:
            self._start_learning_thread()
        
        self.logger.ai("Sistema de aprendizado inicializado")
    
    def _init_database(self):
        """Inicializa banco de dados para armazenar dados de aprendizado"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de interações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    command TEXT NOT NULL,
                    response TEXT,
                    success BOOLEAN,
                    context TEXT,
                    user_feedback INTEGER DEFAULT 0
                )
            ''')
            
            # Tabela de preferências
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Tabela de padrões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    confidence REAL DEFAULT 0.5,
                    last_seen TEXT NOT NULL
                )
            ''')
            
            conn.commit()
    
    def _setup_event_handlers(self):
        """Configura handlers de eventos para aprendizado"""
        if not self.learning_enabled:
            return
        
        self.event_manager.subscribe(Events.USER_INTERACTION, self._on_user_interaction)
        self.event_manager.subscribe(Events.VOICE_COMMAND, self._on_voice_command)
        self.event_manager.subscribe(Events.AI_RESPONSE, self._on_ai_response)
        self.event_manager.subscribe(Events.AUTOMATION_TRIGGERED, self._on_automation_triggered)
    
    def _start_learning_thread(self):
        """Inicia thread de aprendizado em background"""
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_loop)
        self.learning_thread.daemon = True
        self.learning_thread.start()
    
    def _learning_loop(self):
        """Loop principal de aprendizado"""
        import time
        
        while self.learning_active:
            try:
                # Processar dados a cada 5 minutos
                time.sleep(300)
                
                if len(self.interaction_history) > 10:
                    self._process_learning_batch()
                
            except Exception as e:
                self.logger.error(f"Erro no loop de aprendizado: {e}")
                time.sleep(60)  # Aguardar antes de tentar novamente
    
    def _on_user_interaction(self, data):
        """Handler para interações do usuário"""
        if not data:
            return
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'command': data.get('command', ''),
            'response': data.get('response', ''),
            'success': True,  # Assumir sucesso por padrão
            'context': self._get_current_context()
        }
        
        self.interaction_history.append(interaction)
        self._save_interaction(interaction)
        
        # Análise imediata para preferências óbvias
        self._analyze_immediate_preferences(interaction)
    
    def _on_voice_command(self, data):
        """Handler para comandos de voz"""
        if not data:
            return
        
        command = data.get('text', '').lower()
        timestamp = datetime.now()
        
        # Analisar padrões temporais
        hour = timestamp.hour
        weekday = timestamp.weekday()
        
        self.command_patterns[command].append({
            'hour': hour,
            'weekday': weekday,
            'timestamp': timestamp.isoformat()
        })
        
        # Contar frequência de uso
        self.usage_patterns[command] += 1
    
    def _on_ai_response(self, data):
        """Handler para respostas da IA"""
        # Analisar efetividade das respostas
        pass
    
    def _on_automation_triggered(self, data):
        """Handler para automações"""
        if not data:
            return
        
        # Aprender padrões de automação
        action = data.get('action', '')
        context = self._get_current_context()
        
        self._save_automation_pattern(action, context)
    
    def _get_current_context(self):
        """Obtém contexto atual (hora, dia, etc.)"""
        now = datetime.now()
        return {
            'hour': now.hour,
            'weekday': now.weekday(),
            'month': now.month,
            'is_weekend': now.weekday() >= 5
        }
    
    def _analyze_immediate_preferences(self, interaction):
        """Análise imediata de preferências baseada na interação"""
        command = interaction['command'].lower()
        
        # Preferências de iluminação
        if 'luz' in command or 'acender' in command or 'apagar' in command:
            location = self._extract_location(command)
            time_preference = self._categorize_time(datetime.now().hour)
            
            self._update_preference('lighting', f'{location}_{time_preference}', command)
        
        # Preferências de música
        elif 'música' in command or 'tocar' in command:
            genre = self._extract_music_preference(command)
            if genre:
                self._update_preference('music', 'preferred_genre', genre)
        
        # Preferências de temperatura
        elif 'temperatura' in command or 'clima' in command:
            temp_pref = self._extract_temperature_preference(command)
            if temp_pref:
                self._update_preference('climate', 'preferred_temp', temp_pref)
    
    def _extract_location(self, command):
        """Extrai localização do comando"""
        locations = ['sala', 'quarto', 'cozinha', 'banheiro', 'escritório']
        for location in locations:
            if location in command:
                return location
        return 'geral'
    
    def _extract_music_preference(self, command):
        """Extrai preferência musical do comando"""
        genres = {
            'relaxante': ['relaxante', 'calma', 'suave'],
            'energética': ['animada', 'alta', 'energia'],
            'clássica': ['clássica', 'erudita'],
            'pop': ['pop', 'popular'],
            'rock': ['rock', 'pesada']
        }
        
        for genre, keywords in genres.items():
            if any(keyword in command for keyword in keywords):
                return genre
        return None
    
    def _extract_temperature_preference(self, command):
        """Extrai preferência de temperatura"""
        if 'frio' in command or 'gelado' in command:
            return 'frio'
        elif 'quente' in command or 'calor' in command:
            return 'quente'
        elif any(char.isdigit() for char in command):
            # Tentar extrair número
            import re
            numbers = re.findall(r'\d+', command)
            if numbers:
                return numbers[0]
        return None
    
    def _categorize_time(self, hour):
        """Categoriza horário"""
        if 6 <= hour < 12:
            return 'manha'
        elif 12 <= hour < 18:
            return 'tarde'
        elif 18 <= hour < 22:
            return 'noite'
        else:
            return 'madrugada'
    
    def _update_preference(self, category, key, value, confidence=0.7):
        """Atualiza preferência do usuário"""
        pref_key = f"{category}_{key}"
        
        if pref_key not in self.user_preferences:
            self.user_preferences[pref_key] = {
                'value': value,
                'confidence': confidence,
                'frequency': 1,
                'last_updated': datetime.now().isoformat()
            }
        else:
            # Aumentar confiança se valor é repetido
            current = self.user_preferences[pref_key]
            if current['value'] == value:
                current['confidence'] = min(1.0, current['confidence'] + 0.1)
                current['frequency'] += 1
            else:
                # Diminuir confiança se valor é diferente
                current['confidence'] = max(0.1, current['confidence'] - 0.1)
            
            current['last_updated'] = datetime.now().isoformat()
        
        # Salvar no banco
        self._save_preference(category, key, value, self.user_preferences[pref_key]['confidence'])
        
        # Emitir evento de aprendizado
        self.event_manager.emit(Events.PREFERENCE_LEARNED, {
            'category': category,
            'key': key,
            'value': value,
            'confidence': self.user_preferences[pref_key]['confidence']
        })
    
    def _save_interaction(self, interaction):
        """Salva interação no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interactions (timestamp, command, response, success, context)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                interaction['timestamp'],
                interaction['command'],
                interaction['response'],
                interaction['success'],
                json.dumps(interaction['context'])
            ))
            conn.commit()
    
    def _save_preference(self, category, key, value, confidence):
        """Salva preferência no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar se já existe
            cursor.execute('''
                SELECT id FROM preferences WHERE category = ? AND key = ?
            ''', (category, key))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE preferences 
                    SET value = ?, confidence = ?, last_updated = ?
                    WHERE category = ? AND key = ?
                ''', (value, confidence, datetime.now().isoformat(), category, key))
            else:
                cursor.execute('''
                    INSERT INTO preferences (category, key, value, confidence, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                ''', (category, key, value, confidence, datetime.now().isoformat()))
            
            conn.commit()
    
    def _save_automation_pattern(self, action, context):
        """Salva padrão de automação"""
        pattern_data = {
            'action': action,
            'context': context
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patterns (pattern_type, pattern_data, last_seen)
                VALUES (?, ?, ?)
            ''', ('automation', json.dumps(pattern_data), datetime.now().isoformat()))
            conn.commit()
    
    def _load_existing_data(self):
        """Carrega dados existentes do banco"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Carregar preferências
                cursor.execute('SELECT category, key, value, confidence FROM preferences')
                for category, key, value, confidence in cursor.fetchall():
                    pref_key = f"{category}_{key}"
                    self.user_preferences[pref_key] = {
                        'value': value,
                        'confidence': confidence,
                        'frequency': 1
                    }
                
                self.logger.ai(f"Carregadas {len(self.user_preferences)} preferências")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
    
    def _process_learning_batch(self):
        """Processa lote de dados para aprendizado"""
        try:
            # Detectar padrões temporais
            self._detect_temporal_patterns()
            
            # Treinar classificador de comandos
            self._train_command_classifier()
            
            # Detectar rotinas
            self._detect_routine_patterns()
            
            self.logger.ai("Lote de aprendizado processado")
            
        except Exception as e:
            self.logger.error(f"Erro no processamento de aprendizado: {e}")
    
    def _detect_temporal_patterns(self):
        """Detecta padrões temporais nos comandos"""
        for command, occurrences in self.command_patterns.items():
            if len(occurrences) < 3:
                continue
            
            # Analisar horários
            hours = [occ['hour'] for occ in occurrences]
            weekdays = [occ['weekday'] for occ in occurrences]
            
            # Detectar horários preferidos
            hour_counter = Counter(hours)
            preferred_hours = [h for h, count in hour_counter.most_common(2)]
            
            # Detectar dias preferidos
            weekday_counter = Counter(weekdays)
            
            # Salvar padrão detectado
            pattern = {
                'command': command,
                'preferred_hours': preferred_hours,
                'weekday_pattern': dict(weekday_counter),
                'frequency': len(occurrences)
            }
            
            self._save_temporal_pattern(pattern)
    
    def _save_temporal_pattern(self, pattern):
        """Salva padrão temporal detectado"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO patterns (pattern_type, pattern_data, frequency, last_seen)
                VALUES (?, ?, ?, ?)
            ''', (
                'temporal',
                json.dumps(pattern),
                pattern['frequency'],
                datetime.now().isoformat()
            ))
            conn.commit()
    
    def _train_command_classifier(self):
        """Treina classificador de comandos"""
        if len(self.interaction_history) < 20:
            return
        
        try:
            # Preparar dados de treinamento
            commands = [interaction['command'] for interaction in self.interaction_history[-100:]]
            responses = [interaction['response'] for interaction in self.interaction_history[-100:]]
            
            if not commands:
                return
            
            # Vectorizar comandos
            vectorizer = TfidfVectorizer(max_features=100, stop_words=None)
            X = vectorizer.fit_transform(commands)
            
            # Classificar por tipo de resposta/ação
            response_types = []
            for response in responses:
                if 'luz' in response.lower():
                    response_types.append('lighting')
                elif 'temperatura' in response.lower():
                    response_types.append('climate')
                elif 'música' in response.lower():
                    response_types.append('music')
                else:
                    response_types.append('general')
            
            # Treinar classificador
            if len(set(response_types)) > 1:
                classifier = MultinomialNB()
                classifier.fit(X, response_types)
                
                # Salvar modelo
                self.command_classifier = {
                    'vectorizer': vectorizer,
                    'classifier': classifier
                }
                
                self.logger.ai("Classificador de comandos treinado")
            
        except Exception as e:
            self.logger.error(f"Erro ao treinar classificador: {e}")
    
    def _detect_routine_patterns(self):
        """Detecta padrões de rotina do usuário"""
        # Analisar sequências de comandos
        # Detectar rotinas matinais, noturnas, etc.
        pass
    
    def get_user_preference(self, category, key, default=None):
        """Obtém preferência do usuário"""
        pref_key = f"{category}_{key}"
        preference = self.user_preferences.get(pref_key)
        
        if preference and preference['confidence'] > 0.5:
            return preference['value']
        
        return default
    
    def suggest_action(self, current_context=None):
        """Sugere ação baseada no contexto atual e aprendizado"""
        if not current_context:
            current_context = self._get_current_context()
        
        suggestions = []
        
        # Sugestões baseadas em horário
        hour = current_context['hour']
        if 6 <= hour <= 8:  # Manhã
            suggestions.append("Gostaria que eu ligue as luzes da sala?")
            suggestions.append("Posso tocar sua playlist matinal?")
        elif 18 <= hour <= 20:  # Início da noite
            suggestions.append("Hora de acender as luzes? O sol já se pôs.")
            suggestions.append("Que tal ajustar a temperatura para o ambiente noturno?")
        elif 22 <= hour <= 23:  # Noite
            suggestions.append("Deseja ativar o modo noturno?")
            suggestions.append("Posso diminuir as luzes gradualmente?")
        
        return suggestions
    
    def get_learning_stats(self):
        """Retorna estatísticas do aprendizado"""
        return {
            'total_interactions': len(self.interaction_history),
            'preferences_learned': len(self.user_preferences),
            'command_patterns': len(self.command_patterns),
            'learning_enabled': self.learning_enabled,
            'high_confidence_preferences': len([
                p for p in self.user_preferences.values() 
                if p['confidence'] > 0.8
            ])
        }
    
    def shutdown(self):
        """Finaliza sistema de aprendizado"""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=2)
        
        self.logger.ai("Sistema de aprendizado finalizado")