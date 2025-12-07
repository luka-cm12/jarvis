#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Qt Launcher
Launcher simplificado para teste
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Verificar dependências essenciais"""
    missing = []
    
    try:
        import PyQt5
        print("✅ PyQt5 disponível")
    except ImportError:
        missing.append("PyQt5")
    
    try:
        import speech_recognition
        print("✅ SpeechRecognition disponível")
    except ImportError:
        missing.append("SpeechRecognition")
    
    try:
        import pyttsx3
        print("✅ pyttsx3 disponível")
    except ImportError:
        missing.append("pyttsx3")
    
    if missing:
        print(f"\n❌ Dependências faltando: {', '.join(missing)}")
        print("Execute: pip install " + " ".join(missing))
        return False
    
    return True

def main():
    """Função principal"""
    print("🤖 JARVIS PyQt Launcher")
    print("=" * 40)
    
    # Verificar dependências
    if not check_dependencies():
        input("\nPressione Enter para sair...")
        return 1
    
    # Tentar importar e executar
    try:
        from PyQt5.QtWidgets import QApplication
        
        # Adicionar paths
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        sys.path.insert(0, str(current_dir.parent))
        
        # Importar main
        from main import main as jarvis_main
        
        print("\n🚀 Iniciando JARVIS PyQt Interface...")
        return jarvis_main()
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("Verifique se todas as dependências estão instaladas")
        input("\nPressione Enter para sair...")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("\nPressione Enter para sair...")
        return 1

if __name__ == '__main__':
    sys.exit(main())