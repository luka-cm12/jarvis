# JARVIS Advanced Assistant - PyQt Interface

Interface PyQt5 estilo Jarvis do Homem de Ferro com capacidades avançadas de IA, rede e segurança.

## 🎯 Características

- **Interface Jarvis**: Design azul neon, ciano e preto inspirado no filme
- **IA Avançada**: Integração com sistema de IA com aprendizado e análise emocional
- **Reconhecimento de Voz**: Sistema completo de comando por voz em português
- **Scanner de Rede**: Análise avançada de dispositivos e vulnerabilidades
- **Detecção Móvel**: Identificação especializada de dispositivos iOS/Android
- **Sistema de Pentest**: Framework ético de testes de penetração
- **Animações**: Efeitos visuais com brilho, sombras e LEDs animados

## 🚀 Instalação Rápida

1. **Ambiente Virtual** (recomendado):
```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Mac/Linux
```

2. **Instalar Dependências**:
```bash
cd qt_interface
pip install -r requirements.txt
```

3. **Configurar API** em `config/settings.py`:
```python
OPENAI_API_KEY = 'sua_chave_openai_aqui'
```

4. **Executar**:
```bash
python main.py
```

## 📁 Estrutura do Projeto

```
qt_interface/
│
├── core/                    # Lógica principal
│   ├── listener.py         # Reconhecimento de voz
│   ├── responder.py        # Síntese de voz
│   ├── chatbot.py          # IA e ChatGPT
│   └── command_handler.py  # Processamento de comandos
│
├── interface/               # Interface PyQt
│   └── main_ui.py          # Interface principal
│
├── config/                  # Configurações
│   └── settings.py         # Configurações do sistema
│
├── main.py                  # Arquivo principal
├── requirements.txt         # Dependências
└── README.md               # Esta documentação
```

## 🎮 Como Usar

### Comandos de Voz Básicos:
- **"Que horas são"** - Mostra horário atual
- **"Abrir YouTube"** - Abre YouTube no navegador
- **"Tocar música"** - Abre Spotify
- **"Sair"** - Encerra o sistema

### Comandos Avançados de Rede:
- **"Escanear rede"** - Analisa dispositivos na rede
- **"Detectar celulares"** - Encontra dispositivos móveis
- **"Análise de segurança"** - Executa pentest ético

### Interface:
- **Botão LISTEN**: Ativa reconhecimento de voz
- **SCAN NETWORK**: Escaneamento manual de rede
- **DETECT MOBILE**: Detecção de dispositivos móveis
- **SECURITY SCAN**: Análise de vulnerabilidades

### Painel de Controle:
- **Continuous Listening**: Escuta contínua de comandos
- **Auto Network Scan**: Escaneamento automático a cada 30s
- **Voice Feedback**: Respostas por voz ativadas/desativadas

## 🔧 Configurações Avançadas

### Personalizar Cores em `config/settings.py`:
```python
THEME_COLOR = '#4fe0ff'      # Azul neon principal
ACCENT_COLOR = '#00ffd1'     # Ciano
BACKGROUND_COLOR = '#0b0f14' # Fundo escuro
```

### Ajustar Voz:
```python
VOICE_RATE = 150      # Velocidade da fala
VOICE_VOLUME = 1.0    # Volume (0.0 a 1.0)
LANGUAGE = 'pt-BR'    # Idioma reconhecimento
```

### Configurar Rede:
```python
NETWORK_SCAN_RANGE = "192.168.1.0/24"  # Range de scan
AUTO_SCAN_INTERVAL = 30                 # Intervalo auto-scan
```

## 🎨 Recursos Visuais

- **Animações de Brilho**: Botão principal com efeito pulsante
- **LEDs de Status**: Indicadores coloridos por estado
- **Visualização de Rede**: Gráfico em tempo real dos dispositivos
- **Efeitos de Sombra**: Sombras dinâmicas nos elementos
- **Tema Jarvis**: Cores e fontes inspiradas no filme

## ⚠️ Considerações Éticas

Este sistema inclui ferramentas de análise de rede e pentest que devem ser usadas:
- ✅ Apenas em redes próprias ou com autorização
- ✅ Para fins educacionais e de segurança
- ❌ NUNCA para atividades maliciosas
- ❌ NUNCA em redes de terceiros sem permissão

## 🔧 Solução de Problemas

### Erro PyAudio (Windows):
```bash
pip install pipwin
pipwin install pyaudio
```

### Erro OpenAI:
- Verificar chave API em `config/settings.py`
- Verificar conectividade de internet
- Verificar créditos na conta OpenAI

### Erro Microfone:
- Verificar permissões de microfone
- Testar microfone em outras aplicações
- Verificar drivers de áudio

### Performance:
- Fechar outros aplicativos pesados
- Verificar uso de CPU/RAM no painel
- Desativar auto-scan se necessário

## 🤖 Integração com Sistema Web

O JARVIS PyQt pode funcionar junto com o servidor web:

1. **Manter servidor web rodando**: `python start_production.py`
2. **Executar interface PyQt**: `python qt_interface/main.py`
3. **Acessar ambas interfaces**: Desktop (PyQt) + Web (navegador)

## 📋 Dependências Principais

- **PyQt5**: Interface gráfica moderna
- **SpeechRecognition**: Reconhecimento de voz
- **pyttsx3**: Síntese de voz
- **OpenAI**: Integração com ChatGPT
- **python-nmap**: Scanner de rede
- **psutil**: Monitoramento do sistema
- **textblob**: Processamento de linguagem natural

## 📝 Licença

Este projeto é para fins educacionais e de demonstração. Use responsavelmente.

---

**Criado por**: Sistema JARVIS Avançado  
**Versão**: 2.0 PyQt  
**Data**: Dezembro 2025  
**Inspirado em**: Tony Stark's J.A.R.V.I.S. (Iron Man)