#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Sistema de Depuração e Diagnóstico
"""

import sys
import os
import platform
import subprocess
import json
from datetime import datetime
from pathlib import Path

class JarvisDebugger:
    """Sistema de depuração do JARVIS"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def run_full_diagnostic(self):
        """Executar diagnóstico completo do sistema"""
        print("=" * 80)
        print(" " * 25 + "🔍 JARVIS - DIAGNÓSTICO COMPLETO")
        print("=" * 80)
        print()
        
        # Verificações
        self.check_python_version()
        self.check_dependencies()
        self.check_file_structure()
        self.check_network_ports()
        self.check_permissions()
        
        # Relatório final
        self.print_report()
        
        return len(self.issues) == 0
    
    def check_python_version(self):
        """Verificar versão do Python"""
        print("📋 Verificando Python...")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major >= 3 and version.minor >= 8:
            print(f"   ✅ Python {version_str} (OK)")
        else:
            self.issues.append(f"Python {version_str} muito antigo (requer 3.8+)")
            print(f"   ❌ Python {version_str} (INCOMPATÍVEL)")
        
        print(f"   📍 Executável: {sys.executable}")
        print()
    
    def check_dependencies(self):
        """Verificar dependências instaladas"""
        print("📦 Verificando Dependências...")
        
        required = {
            'flask': 'Interface web',
            'flask-socketio': 'WebSocket real-time',
            'fastapi': 'API REST',
            'uvicorn': 'Servidor ASGI',
            'cryptography': 'Segurança',
            'PyQt5': 'Interface gráfica (opcional)'
        }
        
        for package, description in required.items():
            try:
                __import__(package.replace('-', '_'))
                print(f"   ✅ {package:<20} - {description}")
            except ImportError:
                if 'opcional' in description.lower():
                    self.warnings.append(f"{package} não instalado (opcional)")
                    print(f"   ⚠️  {package:<20} - {description}")
                else:
                    self.issues.append(f"{package} não instalado")
                    print(f"   ❌ {package:<20} - {description}")
        print()
    
    def check_file_structure(self):
        """Verificar estrutura de arquivos"""
        print("📁 Verificando Estrutura de Arquivos...")
        
        required_files = [
            'web/app.py',
            'web/templates/index.html',
            'tools/simple_tools.py',
            'tools/ethical_hacker.py',
            'assistant/jarvis_ai.py',
            'start_jarvis.py'
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                print(f"   ✅ {file_path:<35} ({size:,} bytes)")
            else:
                self.issues.append(f"Arquivo não encontrado: {file_path}")
                print(f"   ❌ {file_path:<35} (NÃO ENCONTRADO)")
        print()
    
    def check_network_ports(self):
        """Verificar portas de rede"""
        print("🌐 Verificando Portas de Rede...")
        
        import socket
        
        # Verificar porta 5000 (Flask)
        port = 5000
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Porta {port} - Servidor em execução")
            else:
                self.warnings.append(f"Porta {port} não está em uso")
                print(f"   ℹ️  Porta {port} - Disponível (servidor não iniciado)")
        except Exception as e:
            self.warnings.append(f"Erro ao verificar porta {port}: {e}")
            print(f"   ⚠️  Porta {port} - Erro na verificação")
        
        # Obter IP local
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"   📍 IP Local: {local_ip}")
            print(f"   💡 Acesso celular: http://{local_ip}:5000")
        except:
            self.warnings.append("Não foi possível obter IP local")
            print(f"   ⚠️  IP Local: Não disponível")
        
        print()
    
    def check_permissions(self):
        """Verificar permissões de arquivos"""
        print("🔐 Verificando Permissões...")
        
        # Verificar se pode criar arquivos
        test_file = Path('test_permissions.tmp')
        try:
            test_file.write_text('test')
            test_file.unlink()
            print(f"   ✅ Permissão de escrita OK")
        except Exception as e:
            self.issues.append(f"Sem permissão de escrita: {e}")
            print(f"   ❌ Permissão de escrita NEGADA")
        
        # Verificar se pode executar scripts
        if platform.system() != 'Windows':
            try:
                result = subprocess.run(['whoami'], capture_output=True, text=True, timeout=5)
                user = result.stdout.strip()
                print(f"   ✅ Usuário: {user}")
            except:
                self.warnings.append("Não foi possível verificar usuário")
                print(f"   ⚠️  Usuário: Desconhecido")
        
        print()
    
    def print_report(self):
        """Imprimir relatório final"""
        print("=" * 80)
        print(" " * 30 + "📊 RELATÓRIO FINAL")
        print("=" * 80)
        print()
        
        # Resumo
        total_checks = len(self.issues) + len(self.warnings)
        
        if len(self.issues) == 0:
            print("🟢 STATUS: SISTEMA OPERACIONAL")
            print()
            print("   Todos os componentes essenciais estão funcionando corretamente.")
            print("   O JARVIS está pronto para uso!")
        else:
            print("🔴 STATUS: PROBLEMAS DETECTADOS")
            print()
            print(f"   {len(self.issues)} problema(s) crítico(s) encontrado(s)")
        
        # Problemas críticos
        if self.issues:
            print()
            print("❌ PROBLEMAS CRÍTICOS:")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        # Avisos
        if self.warnings:
            print()
            print("⚠️  AVISOS:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # Sugestões
        if self.issues or self.warnings:
            print()
            print("💡 SOLUÇÕES RECOMENDADAS:")
            print()
            
            if any('não instalado' in issue for issue in self.issues):
                print("   📦 Instalar dependências faltantes:")
                print("      cd jarvis-cyber")
                print("      pip install -r requirements.txt")
                print()
            
            if any('Arquivo não encontrado' in issue for issue in self.issues):
                print("   📁 Verificar se está no diretório correto:")
                print("      cd C:\\xampp\\htdocs\\jarvis\\jarvis-cyber")
                print()
            
            if any('permissão' in issue.lower() for issue in self.issues):
                print("   🔐 Executar como administrador:")
                print("      Botão direito > Executar como administrador")
                print()
        
        print()
        print("=" * 80)
        print()

def test_web_interface():
    """Testar interface web"""
    print("🌐 Testando Interface Web...")
    print()
    
    try:
        # Verificar se Flask está disponível
        import flask
        print("   ✅ Flask importado com sucesso")
        
        # Verificar arquivo app.py
        app_file = Path('web/app.py')
        if app_file.exists():
            print("   ✅ web/app.py encontrado")
            
            # Verificar sintaxe
            try:
                with open(app_file) as f:
                    compile(f.read(), app_file, 'exec')
                print("   ✅ Sintaxe do app.py OK")
            except SyntaxError as e:
                print(f"   ❌ Erro de sintaxe em app.py: linha {e.lineno}")
                print(f"      {e.msg}")
        else:
            print("   ❌ web/app.py não encontrado")
        
        # Verificar template HTML
        template_file = Path('web/templates/index.html')
        if template_file.exists():
            print("   ✅ web/templates/index.html encontrado")
        else:
            print("   ❌ web/templates/index.html não encontrado")
            
    except ImportError:
        print("   ❌ Flask não está instalado")
        print("      Instale com: pip install flask flask-socketio")
    
    print()

def test_assistant():
    """Testar assistente virtual"""
    print("🤖 Testando Assistente Virtual...")
    print()
    
    try:
        from assistant.jarvis_ai import JarvisAssistant
        
        jarvis = JarvisAssistant()
        print("   ✅ JarvisAssistant importado")
        
        # Teste de saudação
        greeting = jarvis.greet("Tony")
        print(f"   ✅ Saudação: {greeting[:50]}...")
        
        # Teste de comando
        result = jarvis.process_command("status")
        if 'response' in result:
            print("   ✅ Processamento de comandos OK")
        else:
            print("   ⚠️  Processamento de comandos com problemas")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar assistente: {e}")
    
    print()

def test_security_tools():
    """Testar ferramentas de segurança"""
    print("🔒 Testando Ferramentas de Segurança...")
    print()
    
    try:
        from tools.simple_tools import run_quick_scan, run_quick_assessment
        
        print("   ✅ simple_tools importado")
        
        # Teste de scan
        result = run_quick_scan("127.0.0.1")
        if 'hosts' in result:
            print("   ✅ Scanner funcionando")
        
        # Teste de hardening
        result = run_quick_assessment()
        if 'overall_score' in result:
            print("   ✅ Hardening funcionando")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar ferramentas: {e}")
    
    print()

def quick_fix():
    """Correções rápidas automáticas"""
    print("🔧 Aplicando Correções Automáticas...")
    print()
    
    # Criar diretórios faltantes
    dirs = ['logs', 'backups', 'data', 'backups/firewall', 'backups/hardening']
    for dir_name in dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Criado: {dir_name}/")
    
    # Verificar requirements.txt
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("   ⚠️  requirements.txt não encontrado")
        print("   💡 Criando requirements.txt básico...")
        
        requirements = """flask==2.3.3
flask-socketio==5.3.6
fastapi==0.109.0
uvicorn==0.27.0
cryptography==41.0.7
httpx==0.25.2
python-socketio==5.8.0"""
        
        req_file.write_text(requirements)
        print("   ✅ requirements.txt criado")
    
    print()
    print("✅ Correções aplicadas!")
    print()

def test_mobile_access():
    """Testar acesso mobile"""
    print("📱 Testando Acesso Mobile (Xiaomi Redmi 9)...")
    print()
    
    import socket
    
    # Obter IP local
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"   📍 IP do Computador: {local_ip}")
        print(f"   🌐 URL para acessar: http://{local_ip}:5000")
        print()
        
        # Verificar se porta está aberta
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("   ✅ Servidor em execução na porta 5000")
            print()
            print("   📱 INSTRUÇÕES PARA XIAOMI REDMI 9:")
            print("   " + "="*50)
            print()
            print("   1. Conecte o celular no mesmo Wi-Fi")
            print("   2. Abra o Chrome no celular")
            print(f"   3. Digite: http://{local_ip}:5000")
            print("   4. Pressione Enter")
            print()
            print("   ⚠️  Se não carregar:")
            print("   • Verifique se ambos estão na mesma rede")
            print("   • Execute: New-NetFirewallRule -DisplayName")
            print("     'JARVIS' -Direction Inbound -Port 5000")
            print("     -Protocol TCP -Action Allow")
            print("   • Reinicie o servidor")
        else:
            print("   ❌ Servidor NÃO está rodando")
            print()
            print("   💡 Para iniciar o servidor:")
            print("      cd jarvis-cyber")
            print("      python web/app.py")
            print("      OU")
            print("      python launch_mobile.py")
        
        print()
        
        # Verificar firewall
        print("   🔥 Verificando Firewall...")
        try:
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                capture_output=True, text=True, timeout=5
            )
            if 'JARVIS' in result.stdout or '5000' in result.stdout:
                print("   ✅ Regra de firewall encontrada")
            else:
                print("   ⚠️  Regra de firewall não encontrada")
                print("   💡 Execute como Administrador:")
                print("      New-NetFirewallRule -DisplayName 'JARVIS Flask'")
                print("      -Direction Inbound -Port 5000 -Protocol TCP -Action Allow")
        except:
            print("   ⚠️  Não foi possível verificar firewall")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print()

def main():
    """Função principal de depuração"""
    print()
    print("🤖 JARVIS - Sistema de Depuração")
    print()
    
    # Menu
    print("Escolha uma opção:")
    print()
    print("1. 🔍 Diagnóstico Completo")
    print("2. 🌐 Testar Interface Web")
    print("3. 🤖 Testar Assistente Virtual")
    print("4. 🔒 Testar Ferramentas de Segurança")
    print("5. 🔧 Aplicar Correções Automáticas")
    print("6. 📋 Executar Todos os Testes")
    print("7. 📱 Testar Acesso Mobile (Xiaomi Redmi 9)")
    print()
    
    choice = input("Digite a opção (1-7): ").strip()
    print()
    
    if choice == '1':
        debugger = JarvisDebugger()
        debugger.run_full_diagnostic()
    elif choice == '2':
        test_web_interface()
    elif choice == '3':
        test_assistant()
    elif choice == '4':
        test_security_tools()
    elif choice == '5':
        quick_fix()
    elif choice == '6':
        debugger = JarvisDebugger()
        debugger.run_full_diagnostic()
        test_web_interface()
        test_assistant()
        test_security_tools()
    elif choice == '7':
        test_mobile_access()
    else:
        print("❌ Opção inválida")
    
    print()
    input("Pressione ENTER para finalizar...")

if __name__ == "__main__":
    main()