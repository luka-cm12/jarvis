# Guia de Instalação do JARVIS

Este guia o ajudará a instalar e configurar o JARVIS em seu sistema Windows.

## 📋 Pré-requisitos

### Sistema Operacional
- Windows 10 ou superior
- 4GB RAM (8GB recomendado)
- 2GB espaço em disco

### Software Necessário
1. **Python 3.9+**
   - Download: https://www.python.org/downloads/
   - ✅ Marque "Add Python to PATH" durante instalação

2. **Microsoft C++ Build Tools** (para PyAudio)
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Ou instale Visual Studio Community

3. **Git** (opcional, para clonagem)
   - Download: https://git-scm.com/download/win

## 🔧 Instalação

### Passo 1: Baixar o Projeto
```bash
# Opção 1: Clone via Git
git clone https://github.com/seu-usuario/jarvis.git
cd jarvis

# Opção 2: Download direto
# Baixe e extraia o ZIP do projeto
```

### Passo 2: Criar Ambiente Virtual
```bash
# Abra PowerShell como Administrador no diretório do projeto
python -m venv venv
venv\Scripts\activate
```

### Passo 3: Instalar Dependências
```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar PyAudio primeiro (pode dar erro, veja solução abaixo)
pip install pyaudio

# Instalar todas as dependências
pip install -r requirements.txt
```

### Solução para Erro do PyAudio
Se der erro no PyAudio:
```bash
# Instalar versão pré-compilada
pip install pipwin
pipwin install pyaudio
```

## ⚙️ Configuração

### Passo 1: Configurar Arquivo de Config
```bash
# Copiar template de configuração
copy config\config.example.json config\config.json
```

### Passo 2: Editar Configurações
Abra `config/config.json` e configure:

#### APIs Necessárias:
```json
{
  "ai": {
    "openai_api_key": "sua-chave-openai-aqui"
  },
  "services": {
    "weather": {
      "api_key": "sua-chave-weather-api"
    }
  }
}
```

#### Obter Chaves API:

**OpenAI API:**
1. Acesse: https://platform.openai.com/
2. Crie conta / faça login
3. Vá em "API Keys"
4. Clique "Create new secret key"
5. Copie a chave para o config

**Weather API (OpenWeatherMap):**
1. Acesse: https://openweathermap.org/api
2. Crie conta gratuita
3. Vá em "My API Keys"
4. Copie a chave padrão

### Passo 3: Configurar Dispositivos (Opcional)

#### Philips Hue:
```json
"home_automation": {
  "philips_hue": {
    "bridge_ip": "IP-DO-SEU-BRIDGE",
    "username": "usuario-hue",
    "enabled": true
  }
}
```

#### Home Assistant:
```json
"home_automation": {
  "home_assistant": {
    "url": "http://SEU-HOME-ASSISTANT:8123",
    "api_token": "seu-token-long-lived",
    "enabled": true
  }
}
```

## 🚀 Primeira Execução

### Teste de Sistema
```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Executar JARVIS
python main.py
```

### Teste de Microfone
O JARVIS testará automaticamente o microfone na primeira execução.

### Interface Web
Abra navegador em: http://localhost:5000

## 🔧 Solução de Problemas

### Erro de Microfone
```bash
# Verificar dispositivos de áudio disponíveis
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

### Erro de Permissões
- Execute PowerShell como Administrador
- Configure política de execução:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Erro de Codec de Áudio
```bash
pip install --upgrade pyaudio
# Ou instalar via conda:
conda install pyaudio
```

### OpenAI API Limits
- Verifique limites em: https://platform.openai.com/usage
- Configure `temperature` e `max_tokens` menores no config

## 📱 Configuração Mobile (Opcional)

Para controle via smartphone:
1. Configure `"host": "0.0.0.0"` no config web
2. Abra porta 5000 no Windows Firewall
3. Acesse pelo IP local: `http://192.168.1.X:5000`

## 🔒 Segurança

### Firewall
```bash
# Permitir Python no firewall (executar como Admin)
netsh advfirewall firewall add rule name="Python JARVIS" dir=in action=allow program="C:\caminho\para\python.exe"
```

### Configurações de Privacidade
- Microfone: Configurações > Privacidade > Microfone
- Marque permissão para aplicativos desktop

## 📊 Logs e Monitoramento

### Visualizar Logs
```bash
# Log em tempo real
Get-Content logs\jarvis.log -Wait -Tail 10

# Ou abra o arquivo em notepad
notepad logs\jarvis.log
```

### Limpeza de Logs
```bash
# Limpar logs antigos
Remove-Item logs\*.log.* -Force
```

## 🔄 Atualizações

### Atualizar Dependências
```bash
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Backup de Configurações
```bash
# Fazer backup antes de atualizar
copy config\config.json config\config.backup.json
copy data\jarvis.db data\jarvis.backup.db
```

## 📞 Suporte

### Logs para Suporte
Ao relatar problemas, inclua:
- Arquivo `logs/jarvis.log`
- Versão do Python: `python --version`
- Sistema operacional e versão

### Comandos de Diagnóstico
```bash
# Informações do sistema
python -c "import sys, platform; print(f'Python: {sys.version}'); print(f'OS: {platform.platform()}')"

# Teste de dependências
python -c "import speech_recognition, pyttsx3, flask; print('Dependências OK')"
```

---

🎉 **Parabéns!** Seu JARVIS está pronto para uso!

**Primeiros comandos para testar:**
- "Jarvis, olá"
- "Acenda as luzes da sala"
- "Que horas são?"
- "Como você está?"