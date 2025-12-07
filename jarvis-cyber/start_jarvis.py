#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS Cyber Security System - Launcher
Script de inicialização principal do sistema
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Exibir banner do JARVIS"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                              ║
    ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                              ║
    ║        ██║███████║██████╔╝██║   ██║██║███████╗                              ║
    ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                              ║
    ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                              ║
    ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                              ║
    ║                                                                              ║
    ║                      CYBER SECURITY SYSTEM                                  ║
    ║                                                                              ║
    ║                    🛡️  Ethical Security Testing  🛡️                          ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Verificar versão do Python"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {major}.{minor}")
        return False
    print(f"✅ Python {major}.{minor}")
    return True

def check_dependencies():
    """Verificar dependências principais"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'PyQt5',
        'cryptography',
        'httpx'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Dependências faltando: {', '.join(missing)}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_nmap():
    """Verificar se nmap está disponível"""
    try:
        result = subprocess.run(['nmap', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ nmap disponível")
            return True
        else:
            print("❌ nmap não encontrado")
            return False
    except FileNotFoundError:
        print("❌ nmap não instalado")
        print("💡 Instale: sudo apt install nmap (Linux) ou baixe de nmap.org")
        return False

def create_directories():
    """Criar diretórios necessários"""
    dirs = ['logs', 'backups', 'data', 'backups/firewall', 'backups/hardening']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Criado diretório: {dir_name}")
        else:
            print(f"✅ Diretório existe: {dir_name}")

def show_menu():
    """Exibir menu de opções"""
    print("\n" + "="*60)
    print("🚀 JARVIS CYBER SECURITY SYSTEM")
    print("="*60)
    print("1. 🌐 Interface Web Responsiva (Desktop + Mobile)")
    print("2. 🖥️  Interface PyQt5 Simplificada") 
    print("3. 🖥️  Interface PyQt5 Completa")
    print("4. ⚡ Servidor API FastAPI")
    print("5. 🤖 Configurar Agente")
    print("6. 🧪 Iniciar Laboratório Docker")
    print("7. 🔍 Teste Rápido de Scanner")
    print("8. 🛡️  Teste de Hardening") 
    print("9. 🔧 Instalar Dependências")
    print("A. ❓ Ajuda")
    print("0. 🚪 Sair")
    print("="*60)

def install_dependencies():
    """Instalar dependências automaticamente"""
    print("📦 Instalando dependências...")
    
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def start_web_interface():
    """Iniciar interface web responsiva"""
    print("🌐 Iniciando interface web responsiva...")
    print("📱 Compatível com Desktop e Mobile")
    print("🌍 Acesse: http://localhost:5000")
    try:
        subprocess.run([sys.executable, 'web/app.py'])
    except Exception as e:
        print(f"❌ Erro ao iniciar interface web: {e}")
        print("💡 Tente instalar: pip install flask flask-socketio")

def start_gui():
    """Iniciar interface gráfica completa"""
    print("🖥️ Iniciando interface gráfica completa...")
    try:
        subprocess.run([sys.executable, 'interface/main_ui.py'])
    except Exception as e:
        print(f"❌ Erro ao iniciar GUI: {e}")
        print("💡 Tente instalar PyQt5: pip install PyQt5")

def start_simple_gui():
    """Iniciar interface gráfica simplificada"""
    print("🖥️ Iniciando interface gráfica simplificada...")
    try:
        subprocess.run([sys.executable, 'interface/jarvis_simple.py'])
    except Exception as e:
        print(f"❌ Erro ao iniciar GUI simplificada: {e}")
        print("💡 Tente instalar PyQt5: pip install PyQt5")

def start_server():
    """Iniciar servidor API"""
    print("🌐 Iniciando servidor API...")
    try:
        subprocess.run([sys.executable, 'server/app.py'])
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

def setup_agent():
    """Configurar agente"""
    print("🤖 Configuração de Agente")
    print("-" * 30)
    
    server_url = input("URL do servidor (http://localhost:8000): ").strip()
    if not server_url:
        server_url = "http://localhost:8000"
    
    agent_name = input("Nome do agente (agent-001): ").strip()
    if not agent_name:
        agent_name = "agent-001"
    
    print(f"Configurando agente '{agent_name}' para '{server_url}'...")
    
    try:
        subprocess.run([
            sys.executable, 'agent/agent.py',
            '--server', server_url,
            '--name', agent_name
        ])
    except Exception as e:
        print(f"❌ Erro ao configurar agente: {e}")

def start_lab():
    """Iniciar laboratório Docker"""
    print("🧪 Iniciando laboratório Docker...")
    
    if not os.path.exists('lab/docker-compose.yml'):
        print("❌ Arquivo docker-compose.yml não encontrado em lab/")
        return
    
    try:
        os.chdir('lab')
        subprocess.run(['docker-compose', 'up', '-d'])
        print("✅ Laboratório iniciado!")
        print("🌐 Acesse:")
        print("   - DVWA: http://localhost:8081")
        print("   - WebGoat: http://localhost:8082") 
        print("   - Portainer: http://localhost:9000")
        os.chdir('..')
    except Exception as e:
        print(f"❌ Erro ao iniciar lab: {e}")
        print("💡 Certifique-se que o Docker está instalado e rodando")

def test_scanner():
    """Teste rápido de scanner"""
    print("🔍 Teste do Scanner")
    print("-" * 20)
    
    try:
        from tools.simple_tools import run_quick_scan
        
        target = input("Alvo para teste (127.0.0.1): ").strip()
        if not target:
            target = "127.0.0.1"
        
        print(f"Testando scan em {target}...")
        result = run_quick_scan(target)
        
        if 'error' in result:
            print(f"❌ Erro: {result['error']}")
        else:
            hosts = result.get('hosts', [])
            print(f"✅ Scan concluído! {len(hosts)} hosts encontrados")
            
            for host in hosts[:3]:  # Mostrar apenas primeiros 3
                ip = host.get('ip', 'unknown')
                ports = len(host.get('open_ports', []))
                print(f"   {ip}: {ports} portas abertas")
                
    except ImportError:
        print("❌ Módulo scanner não disponível")
        print("💡 Instale dependências: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def test_hardening():
    """Teste de hardening"""
    print("🛡️ Teste de Hardening")
    print("-" * 20)
    
    try:
        from tools.simple_tools import run_quick_assessment
        
        print("Executando avaliação de segurança...")
        result = run_quick_assessment()
        
        if 'error' in result:
            print(f"❌ Erro: {result['error']}")
        else:
            score = result.get('overall_score', 0)
            print(f"✅ Score de segurança: {score}/100")
            
            if score >= 80:
                print("🟢 Sistema bem protegido!")
            elif score >= 60:
                print("🟡 Sistema parcialmente protegido")
            else:
                print("🔴 Sistema precisa de melhorias")
            
            recommendations = result.get('recommendations', [])
            if recommendations:
                print("\n📋 Primeiras recomendações:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")
                    
    except ImportError:
        print("❌ Módulo hardening não disponível")
        print("💡 Instale dependências: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def show_help():
    """Exibir ajuda"""
    help_text = """
🆘 AJUDA - JARVIS CYBER SECURITY SYSTEM

📖 DOCUMENTAÇÃO:
   - README.md - Visão geral e instalação
   - docs/runbook.md - Operação e manutenção
   - docs/ - Documentação completa

🚀 INÍCIO RÁPIDO:
   1. pip install -r requirements.txt
   2. Escolha opção 2 (Servidor API)
   3. Em outro terminal, escolha opção 1 (Interface)

🔧 TROUBLESHOOTING:
   - PyQt5 não encontrado: pip install PyQt5
   - nmap não funciona: sudo apt install nmap (Linux)
   - Permissões: Execute como administrador/sudo se necessário

⚖️ IMPORTANTE:
   - Use apenas em redes autorizadas
   - Respeite todas as leis locais
   - Este é um sistema para testes éticos

📧 SUPORTE:
   - GitHub Issues
   - Documentação em docs/
   - Logs em logs/
    """
    print(help_text)

def main():
    """Função principal"""
    print_banner()
    
    print("🔍 Verificando sistema...")
    print("-" * 30)
    
    # Verificações básicas
    if not check_python_version():
        return
    
    # Criar diretórios
    create_directories()
    
    # Verificar dependências
    deps_ok = check_dependencies()
    nmap_ok = check_nmap()
    
    if not deps_ok:
        print("\n⚠️  Sistema não está completamente configurado")
        print("💡 Use a opção 7 para instalar dependências")
    
    # Loop principal
    while True:
        show_menu()
        
        try:
            choice = input("\nEscolha uma opção (0-9, A): ").strip().lower()
            
            if choice == '1':
                start_web_interface()
            elif choice == '2':
                start_simple_gui()
            elif choice == '3':
                start_gui()
            elif choice == '4':
                start_server()
            elif choice == '5':
                setup_agent()
            elif choice == '6':
                start_lab()
            elif choice == '7':
                test_scanner()
            elif choice == '8':
                test_hardening()
            elif choice == '9':
                install_dependencies()
            elif choice == 'a':
                show_help()
            elif choice == '0':
                print("👋 Até logo! Use o JARVIS com responsabilidade.")
                break
            else:
                print("❌ Opção inválida! Escolha entre 1-9.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Saindo do JARVIS...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        input("\n⏸️ Pressione Enter para continuar...")

if __name__ == "__main__":
    main()