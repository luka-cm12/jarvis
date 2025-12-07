#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste do JARVIS
Verifica se todos os componentes estão funcionando
"""

import sys
import os

# Adicionar src ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa importações dos módulos principais"""
    try:
        from core.config_manager import ConfigManager
        from core.logger import setup_logging, JarvisLogger
        from core.events import EventManager, Events
        from ai.brain import AIBrain
        from ai.learning import LearningSystem
        from web.app import JarvisWebInterface
        
        print("✅ Todas as importações funcionaram")
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def test_config():
    """Testa sistema de configuração"""
    try:
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        if config:
            print("✅ Configuração carregada com sucesso")
            print(f"   - Nome: {config.get('jarvis', {}).get('name', 'N/A')}")
            print(f"   - Wake word: {config.get('jarvis', {}).get('wake_word', 'N/A')}")
            return True
        else:
            print("❌ Falha ao carregar configuração")
            return False
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_logging():
    """Testa sistema de logging"""
    try:
        from core.logger import setup_logging, JarvisLogger
        
        setup_logging()
        logger = JarvisLogger('test')
        
        logger.system("Teste do sistema de logging")
        logger.ai("Teste do módulo de IA")
        logger.voice("Teste do módulo de voz")
        
        print("✅ Sistema de logging funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de logging: {e}")
        return False

def test_events():
    """Testa sistema de eventos"""
    try:
        from core.events import EventManager, Events
        
        event_manager = EventManager()
        
        # Teste de callback
        test_data = None
        
        def test_callback(data):
            nonlocal test_data
            test_data = data
        
        event_manager.subscribe('test_event', test_callback)
        event_manager.emit('test_event', {'message': 'teste'})
        
        # Aguardar um pouco para o callback executar
        import time
        time.sleep(0.1)
        
        if test_data and test_data.get('message') == 'teste':
            print("✅ Sistema de eventos funcionando")
            return True
        else:
            print("❌ Sistema de eventos não funcionou corretamente")
            return False
            
    except Exception as e:
        print(f"❌ Erro no sistema de eventos: {e}")
        return False

def test_ai_brain():
    """Testa motor de IA"""
    try:
        from ai.brain import AIBrain
        from core.config_manager import ConfigManager
        
        config = ConfigManager().load_config()
        brain = AIBrain(config)
        
        # Teste de resposta pré-definida
        test_command = "olá"
        response = brain._try_predefined_response(test_command)
        
        if response:
            print(f"✅ Motor de IA funcionando - Resposta para '{test_command}': {response}")
            return True
        else:
            print("❌ Motor de IA não retornou resposta esperada")
            return False
            
    except Exception as e:
        print(f"❌ Erro no motor de IA: {e}")
        return False

def test_learning_system():
    """Testa sistema de aprendizado"""
    try:
        from ai.learning import LearningSystem
        from core.config_manager import ConfigManager
        
        config = ConfigManager().load_config()
        learning = LearningSystem(config)
        
        # Teste básico
        stats = learning.get_learning_stats()
        print(f"✅ Sistema de aprendizado funcionando - Stats: {stats}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de aprendizado: {e}")
        return False

def test_web_interface():
    """Testa interface web"""
    try:
        from web.app import JarvisWebInterface
        from core.config_manager import ConfigManager
        
        config = ConfigManager().load_config()
        web_interface = JarvisWebInterface(config)
        
        print("✅ Interface web pode ser criada")
        return True
        
    except Exception as e:
        print(f"❌ Erro na interface web: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 Executando testes do JARVIS...")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Configuração", test_config),
        ("Sistema de Logging", test_logging),
        ("Sistema de Eventos", test_events),
        ("Motor de IA", test_ai_brain),
        ("Sistema de Aprendizado", test_learning_system),
        ("Interface Web", test_web_interface),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASSOU" if passed_test else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! JARVIS está funcionando corretamente!")
    elif passed >= total * 0.7:
        print("⚠️  Maioria dos testes passou. Alguns problemas menores podem existir.")
    else:
        print("🚨 Muitos testes falharam. Verifique as dependências e configuração.")
    
    return passed == total

if __name__ == "__main__":
    main()