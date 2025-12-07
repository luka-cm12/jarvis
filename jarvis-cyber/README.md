# JARVIS Cyber Security System

## 🚀 Sistema de Cibersegurança Ético Inspirado no JARVIS

![JARVIS Logo](https://img.shields.io/badge/JARVIS-Cyber_Security-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-orange)

### 📋 Visão Geral

O JARVIS Cyber Security System é uma plataforma completa de cibersegurança projetada para operações **éticas e autorizadas**. Inspirado no assistente virtual do Homem de Ferro, oferece ferramentas avançadas para análise, proteção e hardening de sistemas.

### ⚡ Recursos Principais

#### 🔍 Scanner de Rede
- Scan rápido e completo de portas
- Detecção de vulnerabilidades
- Análise de serviços
- Validação ética de alvos

#### 🛡️ Gerenciamento de Firewall
- Configuração automática
- Hardening de sistema
- Backup de configurações
- Suporte multiplataforma

#### 🔒 Hardening de Sistema
- Avaliação de segurança
- Score de compliance
- Recomendações automatizadas
- Correções assistidas

#### 🤖 Sistema de Agentes
- Agentes distribuídos
- Autenticação JWT
- Execução segura de comandos
- Monitoramento remoto

#### 💻 Interface Avançada
- PyQt5 com tema JARVIS
- Interface web moderna
- Logs em tempo real
- Dashboard interativo

### 🏗️ Arquitetura

```
jarvis-cyber/
├── server/           # Servidor FastAPI
├── agent/           # Agentes distribuídos
├── interface/       # Interface PyQt5
├── tools/          # Ferramentas de segurança
├── models/         # IA e modelos locais
├── lab/            # Ambiente de teste
└── docs/           # Documentação
```

### 📦 Instalação

#### Pré-requisitos
- Python 3.8+
- pip
- git

#### Instalação Rápida

```bash
# Clone o repositório
git clone <repository-url>
cd jarvis-cyber

# Instale dependências
pip install -r requirements.txt

# Inicie o servidor
python server/app.py

# Em outro terminal, inicie a interface
python interface/main_ui.py
```

#### Configuração do Ambiente de Teste

```bash
# Inicie laboratório Docker
cd lab
docker-compose up -d

# Verifique serviços
docker-compose ps
```

### 🚀 Uso Rápido

#### 1. Iniciar Servidor
```bash
python server/app.py
```

#### 2. Criar Agente
```bash
python agent/agent.py --server http://localhost:8000
```

#### 3. Executar Interface
```bash
python interface/main_ui.py
```

#### 4. Scanner de Rede
```python
from tools.scanner import run_quick_scan

# Scan ético (apenas redes privadas)
result = run_quick_scan("192.168.1.0/24")
print(result)
```

#### 5. Hardening de Sistema
```python
from tools.hardening import run_quick_assessment

# Avaliação de segurança
assessment = run_quick_assessment()
print(f"Score: {assessment['overall_score']}/100")
```

### 🛡️ Diretrizes Éticas

> **IMPORTANTE: Este sistema deve ser usado APENAS para:**
> - Testes autorizados em suas próprias redes
> - Avaliações de segurança com permissão explícita
> - Ambientes de laboratório e aprendizado
> - Hardening de sistemas próprios

#### ❌ Uso Proibido
- Scans não autorizados
- Ataques a sistemas de terceiros
- Violação de privacidade
- Atividades ilegais

### 📊 Exemplos de Uso

#### Scanner de Vulnerabilidades
```python
from tools.scanner import SecureScanner

scanner = SecureScanner()

# Validar alvo antes do scan
is_valid, error = scanner.validate_target("192.168.1.100")
if is_valid:
    result = scanner.scan_vulnerabilities("192.168.1.100")
    print(f"Vulnerabilidades: {len(result['vulnerabilities'])}")
```

#### Firewall Hardening
```python
from tools.firewall import apply_basic_hardening

# Dry-run primeiro (recomendado)
result = apply_basic_hardening(dry_run=True)
print("Comandos que seriam executados:")
for cmd in result['recommended_commands']:
    print(f"  {cmd}")
```

#### Avaliação de Segurança
```python
from tools.hardening import SystemHardening

hardening = SystemHardening()
assessment = hardening.run_security_assessment()

print(f"Score geral: {assessment['overall_score']}/100")
print("\nRecomendações:")
for rec in assessment['recommendations'][:5]:
    print(f"• {rec}")
```

### 🔧 Configuração Avançada

#### Variáveis de Ambiente
```bash
export JARVIS_SERVER_PORT=8000
export JARVIS_DEBUG=true
export JARVIS_LOG_LEVEL=INFO
export OPENAI_API_KEY=your_key_here
```

#### Arquivo de Configuração
```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "cors_enabled": true
  },
  "security": {
    "jwt_secret": "your-secret-key",
    "token_expiry": 3600,
    "max_scan_range": 1024
  },
  "features": {
    "ai_enabled": true,
    "voice_enabled": false,
    "lab_mode": true
  }
}
```

### 📈 Monitoramento

#### Logs do Sistema
```bash
# Logs do servidor
tail -f logs/server.log

# Logs de segurança
tail -f logs/security.log

# Logs de agentes
tail -f logs/agents.log
```

#### Métricas
- Scans executados
- Vulnerabilidades detectadas
- Hardening aplicado
- Agentes ativos

### 🧪 Laboratório de Testes

O sistema inclui um laboratório Docker com:

- **Metasploitable2**: Sistema Linux vulnerável
- **DVWA**: Aplicação web vulnerável
- **WebGoat**: Ambiente de treinamento
- **Kali Linux**: Ferramentas de teste
- **MySQL**: Banco de dados para testes

```bash
# Iniciar laboratório
cd lab
docker-compose up -d

# Acessar ambientes
# DVWA: http://localhost:8081
# WebGoat: http://localhost:8082
# Portainer: http://localhost:9000
```

### 🔍 Solução de Problemas

#### Erro de Permissão (Scanner)
```bash
# Linux/macOS
sudo python tools/scanner.py

# Ou usar nmap sem sudo
echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/nmap" | sudo tee -a /etc/sudoers
```

#### PyQt5 não encontrado
```bash
pip install PyQt5
# ou
pip install PySide2
```

#### Firewall não detectado
- Instalar UFW (Ubuntu): `sudo apt install ufw`
- Verificar Windows Firewall: Executar como administrador

### 📚 Documentação

- [Guia de Instalação](docs/installation.md)
- [Manual do Usuário](docs/user_guide.md)
- [Referência da API](docs/api_reference.md)
- [Diretrizes de Segurança](docs/security_guidelines.md)
- [Runbook Operacional](docs/runbook.md)

### 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

#### Diretrizes de Desenvolvimento
- Seguir princípios de segurança by design
- Documentar funcionalidades
- Incluir testes automatizados
- Respeitar diretrizes éticas

### 📄 Licença

Este projeto está licenciado sob a MIT License. Veja [LICENSE](LICENSE) para detalhes.

### ⚠️ Disclaimer

**Este software é fornecido "como está", sem garantias. Os usuários são responsáveis por:**
- Usar apenas em sistemas autorizados
- Cumprir todas as leis locais
- Não causar danos a terceiros
- Manter princípios éticos

### 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentação**: `docs/`
- **Exemplos**: `examples/`
- **Chat**: Discord/Slack (se disponível)

### 🎯 Roadmap

#### v1.1
- [ ] Integração com SIEM
- [ ] Relatórios PDF
- [ ] API REST completa
- [ ] Dashboard web avançado

#### v1.2
- [ ] Machine Learning para detecção
- [ ] Integrações cloud (AWS/Azure)
- [ ] Mobile app companion
- [ ] Clustering de agentes

---

**🤖 "I am JARVIS - Your Cyber Security Assistant"**

> Sistema desenvolvido para profissionais de segurança éticos. Use com responsabilidade.