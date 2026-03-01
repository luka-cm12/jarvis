#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS - Launcher para Celular
Gera QR Code e instruções para acesso mobile
"""

import socket
import os

def get_local_ip():
    """Obter IP local da máquina"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "Não foi possível obter IP"

def generate_qr_code(url):
    """Gerar QR Code ASCII para acesso rápido"""
    try:
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii()
        return True
    except ImportError:
        return False

def show_mobile_instructions():
    """Mostrar instruções para acesso mobile"""
    
    local_ip = get_local_ip()
    url = f"http://{local_ip}:5000"
    
    print("=" * 80)
    print(" " * 20 + "🤖 JARVIS - ACESSO VIA CELULAR 📱")
    print("=" * 80)
    print()
    
    print("📱 INSTRUÇÕES PARA CONECTAR SEU CELULAR:")
    print()
    print("   PASSO 1: Conecte seu celular na MESMA rede Wi-Fi do computador")
    print("   PASSO 2: Abra o navegador no celular (Chrome, Safari, Firefox...)")
    print("   PASSO 3: Digite o endereço abaixo:")
    print()
    print("   " + "─" * 60)
    print(f"   📍 {url}")
    print("   " + "─" * 60)
    print()
    
    print("💡 RECURSOS NO CELULAR:")
    print("   ✅ Interface responsiva (adapta-se à tela)")
    print("   ✅ Comandos de voz (usando microfone do celular)")
    print("   ✅ Assistente virtual JARVIS completo")
    print("   ✅ Scanner de rede e testes de segurança")
    print("   ✅ Criar projetos (websites, APIs, scripts)")
    print()
    
    print("🔧 INFORMAÇÕES TÉCNICAS:")
    print(f"   🖥️  IP do Computador: {local_ip}")
    print(f"   🌐 Porta: 5000")
    print(f"   📡 Protocolo: HTTP")
    print()
    
    # Tentar gerar QR Code
    print("📸 QR CODE:")
    if generate_qr_code(url):
        print("   ✅ Escaneie o QR Code acima com a câmera do celular!")
    else:
        print("   ℹ️  QR Code não disponível (instale: pip install qrcode)")
        print(f"   💡 Digite manualmente: {url}")
    print()
    
    print("⚠️  PROBLEMAS COMUNS:")
    print()
    print("   ❌ Não consegue acessar?")
    print("      • Certifique-se que celular e PC estão na mesma rede Wi-Fi")
    print("      • Verifique se o firewall não está bloqueando a porta 5000")
    print("      • No Windows: execute como administrador se necessário")
    print()
    print("   ❌ Comandos de voz não funcionam?")
    print("      • Permita acesso ao microfone no navegador do celular")
    print("      • Use HTTPS em produção (localhost permite HTTP)")
    print()
    
    print("🚀 DICA AVANÇADA:")
    print("   Para acesso externo (fora da rede local), use:")
    print("   • Ngrok: ngrok http 5000")
    print("   • Configurar port forwarding no roteador")
    print()
    
    print("=" * 80)
    print()
    
    return url

if __name__ == "__main__":
    show_mobile_instructions()
    
    print("🎯 PRÓXIMO PASSO:")
    print("   Execute: python web/app.py")
    print()
    
    input("Pressione ENTER para iniciar o servidor JARVIS...")
    
    # Iniciar servidor
    os.system("python web/app.py")