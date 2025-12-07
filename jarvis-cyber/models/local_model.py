#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security - Local Model Wrapper
Wrapper para LLM local ou OpenAI com integração de segurança
"""

import os
import logging
import time
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jarvis.model')

# Configurações
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
USE_LOCAL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "./models/ggml-model.bin")
GPT4ALL_MODEL_PATH = os.getenv("GPT4ALL_MODEL_PATH", "./models/gpt4all-model.bin")

class LocalModelWrapper:
    """
    Wrapper para modelos LLM locais ou OpenAI
    Prioriza segurança e monitoramento de uso
    """
    
    def __init__(self):
        self.use_local = USE_LOCAL
        self.model_type = None
        self.model = None
        self.openai = None
        
        # Estatísticas de uso
        self.request_count = 0
        self.total_tokens = 0
        self.start_time = time.time()
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Inicializar modelo baseado na configuração"""
        if self.use_local:
            self._try_local_models()
        
        # Fallback para OpenAI se local não funcionar
        if not self.model and OPENAI_KEY:
            self._initialize_openai()
        
        if not self.model and not self.openai:
            logger.warning("Nenhum modelo disponível. Sistema funcionará com respostas limitadas.")
    
    def _try_local_models(self):
        """Tentar carregar modelos locais"""
        # Tentar llama.cpp
        try:
            from llama_cpp import Llama
            if os.path.exists(LLAMA_MODEL_PATH):
                logger.info(f"Carregando modelo Llama.cpp: {LLAMA_MODEL_PATH}")
                self.model = Llama(
                    model_path=LLAMA_MODEL_PATH,
                    n_ctx=2048,
                    n_threads=4,
                    verbose=False
                )
                self.model_type = "llama.cpp"
                logger.info("✅ Modelo Llama.cpp carregado com sucesso")
                return
        except ImportError:
            logger.info("llama.cpp não disponível")
        except Exception as e:
            logger.error(f"Erro ao carregar Llama.cpp: {e}")
        
        # Tentar GPT4All
        try:
            from gpt4all import GPT4All
            if os.path.exists(GPT4ALL_MODEL_PATH):
                logger.info(f"Carregando modelo GPT4All: {GPT4ALL_MODEL_PATH}")
                self.model = GPT4All(GPT4ALL_MODEL_PATH)
                self.model_type = "gpt4all"
                logger.info("✅ Modelo GPT4All carregado com sucesso")
                return
        except ImportError:
            logger.info("GPT4All não disponível")
        except Exception as e:
            logger.error(f"Erro ao carregar GPT4All: {e}")
        
        # Tentar Transformers (Hugging Face)
        try:
            from transformers import pipeline
            logger.info("Carregando modelo Hugging Face...")
            self.model = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                device=-1  # CPU
            )
            self.model_type = "transformers"
            logger.info("✅ Modelo Hugging Face carregado com sucesso")
            return
        except ImportError:
            logger.info("Transformers não disponível")
        except Exception as e:
            logger.error(f"Erro ao carregar Transformers: {e}")
        
        logger.warning("Nenhum modelo local pôde ser carregado")
    
    def _initialize_openai(self):
        """Inicializar cliente OpenAI"""
        try:
            import openai
            openai.api_key = OPENAI_KEY
            self.openai = openai
            self.model_type = "openai"
            logger.info("✅ Cliente OpenAI configurado")
        except ImportError:
            logger.error("Biblioteca openai não disponível")
        except Exception as e:
            logger.error(f"Erro ao configurar OpenAI: {e}")
    
    def chat(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Gerar resposta usando o modelo disponível
        
        Args:
            prompt: Prompt de entrada
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura para geração
        
        Returns:
            Resposta gerada
        """
        self.request_count += 1
        start_time = time.time()
        
        try:
            # Filtro de segurança no prompt
            if self._is_malicious_prompt(prompt):
                logger.warning("Prompt potencialmente malicioso detectado")
                return "Desculpe, não posso processar essa solicitação por motivos de segurança."
            
            response = self._generate_response(prompt, max_tokens, temperature)
            
            # Log de uso
            duration = time.time() - start_time
            self._log_usage(prompt, response, duration)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return f"Erro ao processar solicitação: {str(e)}"
    
    def _generate_response(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gerar resposta usando modelo específico"""
        if self.model_type == "llama.cpp":
            return self._generate_llama(prompt, max_tokens, temperature)
        elif self.model_type == "gpt4all":
            return self._generate_gpt4all(prompt, max_tokens, temperature)
        elif self.model_type == "transformers":
            return self._generate_transformers(prompt, max_tokens, temperature)
        elif self.model_type == "openai":
            return self._generate_openai(prompt, max_tokens, temperature)
        else:
            return self._generate_fallback(prompt)
    
    def _generate_llama(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gerar resposta com llama.cpp"""
        try:
            response = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
            return response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"Erro llama.cpp: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_gpt4all(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gerar resposta com GPT4All"""
        try:
            response = self.model.generate(prompt, max_tokens=max_tokens, temp=temperature)
            return response.strip()
        except Exception as e:
            logger.error(f"Erro GPT4All: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_transformers(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gerar resposta com Transformers"""
        try:
            response = self.model(
                prompt, 
                max_length=len(prompt.split()) + max_tokens,
                temperature=temperature,
                do_sample=True
            )
            return response[0]['generated_text'][len(prompt):].strip()
        except Exception as e:
            logger.error(f"Erro Transformers: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_openai(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Gerar resposta com OpenAI"""
        try:
            # Usar ChatCompletion se disponível
            if hasattr(self.openai, 'ChatCompletion'):
                response = self.openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            else:
                # Fallback para Completion
                response = self.openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].text.strip()
                
        except Exception as e:
            logger.error(f"Erro OpenAI: {e}")
            return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Resposta fallback quando modelos não estão disponíveis"""
        prompt_lower = prompt.lower()
        
        # Respostas para segurança
        if any(word in prompt_lower for word in ['scan', 'nmap', 'portscan']):
            return "Para realizar scans, use os comandos autorizados através do agente JARVIS. Certifique-se de ter autorização para o alvo."
        
        if any(word in prompt_lower for word in ['firewall', 'iptables', 'ufw']):
            return "Para configurações de firewall, use os comandos de hardening do agente JARVIS. Sempre faça backup antes de alterar regras."
        
        if any(word in prompt_lower for word in ['vulnerability', 'exploit', 'cve']):
            return "Para análise de vulnerabilidades, use os scans autorizados e consulte bases como CVE/NVD. Mantenha sistemas atualizados."
        
        if any(word in prompt_lower for word in ['logs', 'syslog', 'audit']):
            return "Para análise de logs, use os comandos de verificação do agente JARVIS. Monitore logs de segurança regularmente."
        
        # Resposta genérica
        return "Sistema de IA não disponível no momento. Use os comandos disponíveis através do agente JARVIS para operações de segurança."
    
    def _is_malicious_prompt(self, prompt: str) -> bool:
        """Detectar prompts potencialmente maliciosos"""
        malicious_patterns = [
            'hack into',
            'break into',
            'steal password',
            'ddos attack',
            'sql injection',
            'buffer overflow',
            'privilege escalation',
            'backdoor',
            'rootkit'
        ]
        
        prompt_lower = prompt.lower()
        return any(pattern in prompt_lower for pattern in malicious_patterns)
    
    def _log_usage(self, prompt: str, response: str, duration: float):
        """Registrar uso do modelo"""
        # Estimar tokens (aproximação simples)
        prompt_tokens = len(prompt.split())
        response_tokens = len(response.split())
        total_tokens = prompt_tokens + response_tokens
        
        self.total_tokens += total_tokens
        
        logger.info(f"Model usage - Type: {self.model_type}, Tokens: {total_tokens}, Duration: {duration:.2f}s")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obter informações do modelo"""
        uptime = time.time() - self.start_time
        
        return {
            "type": self.model_type,
            "available": self.model is not None or self.openai is not None,
            "requests": self.request_count,
            "total_tokens": self.total_tokens,
            "uptime_seconds": uptime,
            "avg_tokens_per_request": self.total_tokens / max(self.request_count, 1)
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de uso"""
        return {
            "model_type": self.model_type,
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens,
            "uptime_hours": (time.time() - self.start_time) / 3600,
            "requests_per_hour": self.request_count / max((time.time() - self.start_time) / 3600, 0.001)
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do modelo"""
        try:
            test_prompt = "Test prompt for health check"
            start_time = time.time()
            response = self.chat(test_prompt, max_tokens=10)
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "model_type": self.model_type,
                "response_time": duration,
                "test_successful": len(response) > 0
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model_type": self.model_type,
                "error": str(e)
            }

if __name__ == "__main__":
    # Teste do wrapper
    print("=== JARVIS Model Wrapper Test ===")
    
    model = LocalModelWrapper()
    print(f"Modelo inicializado: {model.model_type}")
    
    # Teste de resposta
    test_prompt = "Como verificar se um sistema está seguro?"
    response = model.chat(test_prompt)
    print(f"\nPrompt: {test_prompt}")
    print(f"Resposta: {response}")
    
    # Estatísticas
    stats = model.get_usage_stats()
    print(f"\nEstatísticas: {stats}")
    
    # Health check
    health = model.health_check()
    print(f"Saúde: {health}")