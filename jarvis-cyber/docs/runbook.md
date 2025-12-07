# JARVIS Cyber Security - Runbook Operacional

## 🔧 Guia de Operação e Manutenção

### 📋 Índice
1. [Inicialização do Sistema](#inicialização-do-sistema)
2. [Operações Diárias](#operações-diárias)
3. [Monitoramento](#monitoramento)
4. [Troubleshooting](#troubleshooting)
5. [Manutenção](#manutenção)
6. [Diretrizes Legais](#diretrizes-legais)

---

## 🚀 Inicialização do Sistema

### Pré-requisitos de Sistema
```bash
# Verificar Python
python --version  # Deve ser 3.8+

# Verificar dependências essenciais
pip list | grep -E "(fastapi|PyQt5|nmap|cryptography)"

# Verificar nmap (necessário para scanner)
nmap --version

# Verificar firewall (Linux)
ufw --version
# ou (CentOS/RHEL)
firewall-cmd --version
```

### Sequência de Startup

#### 1. Preparar Ambiente
```bash
# Definir variáveis de ambiente
export JARVIS_ENV="production"
export JARVIS_LOG_LEVEL="INFO"
export JARVIS_SERVER_PORT="8000"

# Criar diretórios necessários
mkdir -p logs backups data

# Verificar permissões
ls -la logs/ backups/ data/
```

#### 2. Iniciar Servidor Principal
```bash
# Em terminal dedicado
cd jarvis-cyber/
python server/app.py

# Verificar inicialização
curl http://localhost:8000/health
# Esperado: {"status": "healthy", "timestamp": "..."}
```

#### 3. Configurar Agentes (Opcional)
```bash
# Em outro terminal
python agent/agent.py --config agent_config.json

# Verificar conectividade
curl http://localhost:8000/api/agents/status
```

#### 4. Interface de Usuário
```bash
# Terminal dedicado para UI
python interface/main_ui.py
# ou modo web
python interface/web_ui.py
```

---

## 📊 Operações Diárias

### Checklist Matinal (09:00)
- [ ] Verificar status dos serviços
- [ ] Revisar logs de segurança da noite
- [ ] Validar conectividade dos agentes
- [ ] Verificar atualizações de segurança
- [ ] Confirmar backups automáticos

### Comandos de Verificação
```bash
# Status dos serviços
systemctl status jarvis-server  # Se usando systemd
ps aux | grep "python.*jarvis"

# Logs recentes
tail -50 logs/server.log
tail -50 logs/security.log
tail -20 logs/agents.log

# Conectividade
curl -s http://localhost:8000/api/health | jq
curl -s http://localhost:8000/api/agents/list | jq

# Espaço em disco
df -h
du -sh logs/ backups/
```

### Operações de Scanner

#### Scan Autorizado de Rede Interna
```python
# Exemplo de script diário
from tools.scanner import SecureScanner

scanner = SecureScanner()

# Validar alvo (SEMPRE FAZER ISSO)
target = "192.168.1.0/24"  # Apenas redes internas!
is_valid, error = scanner.validate_target(target)

if is_valid:
    print(f"✅ Alvo válido: {target}")
    
    # Scan básico
    result = scanner.scan_host_basic(target)
    hosts_up = len([h for h in result.get('hosts', []) if h.get('state') == 'up'])
    print(f"Hosts ativos: {hosts_up}")
    
    # Scan de portas (apenas hosts conhecidos)
    for host_ip in known_internal_hosts:
        port_result = scanner.scan_ports_quick(host_ip)
        print(f"{host_ip}: {len(port_result.get('hosts', [{}])[0].get('open_ports', []))} portas abertas")
else:
    print(f"❌ Alvo inválido: {error}")
```

#### ⚠️ REGRAS CRÍTICAS PARA SCANNER
1. **NUNCA** fazer scan de IPs públicos sem autorização
2. **SEMPRE** validar alvos antes do scan
3. **DOCUMENTAR** todos os scans em logs
4. **USAR** apenas em redes próprias ou autorizadas
5. **RESPEITAR** limites de taxa e timeout

### Operações de Hardening

#### Avaliação Diária de Segurança
```python
from tools.hardening import SystemHardening

hardening = SystemHardening()
assessment = hardening.run_security_assessment()

print(f"Score de segurança: {assessment['overall_score']}/100")

# Alertar se score baixo
if assessment['overall_score'] < 70:
    print("🚨 ATENÇÃO: Score de segurança baixo!")
    for rec in assessment['recommendations'][:3]:
        print(f"  • {rec}")
```

#### Aplicar Hardening (Com Cuidado)
```python
from tools.firewall import FirewallManager

manager = FirewallManager()

# SEMPRE fazer dry-run primeiro
result = manager.apply_basic_hardening(dry_run=True)
print("Comandos que seriam executados:")
for cmd_result in result['results']:
    print(f"  {cmd_result['command']}")

# Confirmar com operador antes de aplicar
response = input("Aplicar hardening real? (yes/no): ")
if response.lower() == 'yes':
    # Fazer backup primeiro
    backup_file = manager.backup_current_config()
    print(f"Backup criado: {backup_file}")
    
    # Aplicar hardening
    real_result = manager.apply_basic_hardening(dry_run=False)
    print(f"Hardening aplicado. Resultado: {real_result['commands_executed']} comandos")
```

---

## 📈 Monitoramento

### Métricas Importantes

#### Servidor
```bash
# CPU e memória
top -p $(pgrep -f "python.*server")
ps -p $(pgrep -f "python.*server") -o pid,ppid,cmd,%mem,%cpu

# Conexões de rede
netstat -tulpn | grep :8000
ss -tulpn | grep :8000

# Logs por severidade
grep -c "ERROR" logs/server.log
grep -c "WARNING" logs/server.log
grep -c "INFO" logs/server.log
```

#### Agentes
```bash
# Status dos agentes
curl -s http://localhost:8000/api/agents/list | jq '.[] | {id, status, last_seen}'

# Comandos executados pelos agentes
curl -s http://localhost:8000/api/commands/history | jq -r '.[-5:][] | "\(.timestamp) - \(.command)"'
```

### Alertas Automáticos

#### Script de Monitoramento
```bash
#!/bin/bash
# monitor_jarvis.sh

LOG_FILE="/var/log/jarvis_monitor.log"
ALERT_EMAIL="security@company.com"

# Verificar se servidor está rodando
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "$(date) - ALERT: Servidor JARVIS não responsivo" >> $LOG_FILE
    echo "Servidor JARVIS falhou" | mail -s "JARVIS Down" $ALERT_EMAIL
fi

# Verificar uso de disco
DISK_USAGE=$(df /var/log | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date) - WARNING: Uso de disco alto: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Verificar logs de erro
ERROR_COUNT=$(grep -c "ERROR" logs/server.log | tail -1)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "$(date) - WARNING: Muitos erros no servidor: $ERROR_COUNT" >> $LOG_FILE
fi
```

### Dashboards Recomendados

#### Grafana Queries (se disponível)
```
# Scans por hora
rate(jarvis_scans_total[1h])

# Agentes ativos
jarvis_agents_active

# Score de segurança médio
avg(jarvis_security_score)

# Comandos executados
rate(jarvis_commands_total[5m])
```

---

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Servidor não inicia
```bash
# Verificar porta em uso
netstat -tulpn | grep :8000
lsof -i :8000

# Verificar logs de erro
tail -50 logs/server.log | grep ERROR

# Verificar dependências
pip check
python -c "import fastapi, uvicorn; print('OK')"

# Solução comum
pkill -f "python.*server"
python server/app.py
```

#### 2. Scanner não funciona
```bash
# Verificar nmap
which nmap
nmap --version

# Verificar permissões
ls -la $(which nmap)
# Deve ter setuid: -rwsr-xr-x

# Instalar nmap corretamente (Ubuntu)
sudo apt update && sudo apt install nmap

# Teste básico
nmap -sn 127.0.0.1
```

#### 3. Firewall errors
```bash
# Ubuntu/Debian
sudo ufw status
sudo systemctl status ufw

# CentOS/RHEL
sudo firewall-cmd --state
sudo systemctl status firewalld

# Windows (PowerShell como Admin)
Get-NetFirewallProfile
```

#### 4. PyQt5 crashes
```bash
# Verificar display (Linux)
echo $DISPLAY
xhost +local:

# Reinstalar PyQt5
pip uninstall PyQt5
pip install PyQt5

# Alternativa: usar interface web
python interface/web_ui.py
```

#### 5. Agentes desconectam
```bash
# Verificar conectividade
curl http://localhost:8000/api/health

# Verificar token do agente
grep "token" agent/agent_config.json

# Regenerar credenciais
python -c "from server.auth import generate_agent_credentials; print(generate_agent_credentials('agent-001'))"
```

### Logs de Debug

#### Ativar logging detalhado
```python
# server/app.py - adicionar no início
import logging
logging.basicConfig(level=logging.DEBUG)

# ou via variável de ambiente
export JARVIS_LOG_LEVEL=DEBUG
python server/app.py
```

#### Logs estruturados
```bash
# Filtrar por componente
grep "scanner" logs/server.log | tail -20
grep "firewall" logs/server.log | tail -20
grep "hardening" logs/server.log | tail -20

# Filtrar por severidade
grep "ERROR" logs/server.log | tail -10
grep "WARNING" logs/server.log | tail -10

# Filtrar por timestamp (últimas 2 horas)
grep "$(date -d '2 hours ago' '+%Y-%m-%d %H')" logs/server.log
```

---

## 🛠️ Manutenção

### Manutenção Semanal

#### Domingo (02:00)
```bash
#!/bin/bash
# manutencao_semanal.sh

echo "Iniciando manutenção semanal JARVIS..."

# Backup de configurações
tar -czf "backups/config_$(date +%Y%m%d).tar.gz" server/ agent/ interface/

# Rotação de logs
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
find logs/ -name "*.log.gz" -mtime +30 -delete

# Limpeza de dados temporários
rm -rf /tmp/jarvis_*
rm -rf data/temp/*

# Verificar integridade dos backups
for backup in backups/*.tar.gz; do
    if ! tar -tzf "$backup" > /dev/null 2>&1; then
        echo "ERRO: Backup corrompido: $backup"
    fi
done

# Atualizar dependências (cuidado em produção)
# pip list --outdated

echo "Manutenção semanal concluída."
```

### Manutenção Mensal

#### Primeiro sábado do mês
```bash
#!/bin/bash
# manutencao_mensal.sh

# Análise de segurança completa
python tools/hardening.py --full-assessment > reports/security_$(date +%Y%m).txt

# Backup completo do sistema
tar -czf "backups/full_system_$(date +%Y%m%d).tar.gz" \
    server/ agent/ interface/ tools/ models/ docs/ \
    --exclude="*.pyc" --exclude="__pycache__"

# Verificar tamanho dos logs e arquivos
du -sh logs/ data/ backups/

# Gerar relatório de uso
python scripts/generate_usage_report.py > reports/usage_$(date +%Y%m).json

# Verificar atualizações de segurança
pip list --outdated | grep -E "(crypto|security|auth)"

# Teste de recuperação (dry-run)
python scripts/test_backup_restore.py --dry-run
```

### Atualização do Sistema

#### Processo de Update
```bash
# 1. Backup completo
tar -czf "backups/pre_update_$(date +%Y%m%d).tar.gz" jarvis-cyber/

# 2. Parar serviços
pkill -f "python.*jarvis"

# 3. Baixar atualizações
git fetch origin main
git diff HEAD..origin/main

# 4. Aplicar updates
git merge origin/main

# 5. Atualizar dependências
pip install -r requirements.txt

# 6. Migrar configurações (se necessário)
python scripts/migrate_config.py

# 7. Testar em modo debug
export JARVIS_ENV="test"
python server/app.py &
sleep 5
curl http://localhost:8000/health

# 8. Voltar à produção
export JARVIS_ENV="production"
python server/app.py
```

---

## ⚖️ Diretrizes Legais

### ❗ COMPLIANCE E RESPONSABILIDADES

#### Uso Autorizado APENAS
```
✅ PERMITIDO:
- Testes em redes próprias
- Scans com autorização escrita
- Ambientes de laboratório
- Hardening de sistemas próprios
- Treinamento e educação

❌ PROIBIDO:
- Scans não autorizados
- Ataques a terceiros
- Violation de privacidade
- Atividades ilegais
- Uso malicioso
```

#### Documentação Obrigatória
```bash
# Log de autorização para cada operação
echo "$(date) - SCAN AUTORIZADO - Rede: 192.168.1.0/24 - Aprovado por: João Silva - Ticket: SEC-2024-001" >> logs/authorization.log

# Relatório de atividades
python scripts/generate_activity_report.py --date=$(date +%Y-%m-%d) > reports/activity_$(date +%Y%m%d).txt
```

#### Retenção de Logs
- **Logs de segurança**: 1 ano
- **Logs de atividade**: 6 meses
- **Relatórios**: 2 anos
- **Autorizações**: 3 anos

### 📋 Checklist de Compliance

Antes de qualquer operação:
- [ ] Autorização documentada obtida
- [ ] Alvo validado como interno/autorizado
- [ ] Impacto avaliado
- [ ] Janela de manutenção aprovada
- [ ] Plano de rollback preparado
- [ ] Logs habilitados
- [ ] Equipe notificada

### 🚨 Procedimentos de Emergência

#### Em caso de uso não autorizado detectado:
1. **Parar imediatamente** todas as operações
2. **Documentar** o incidente
3. **Notificar** responsáveis de segurança
4. **Investigar** a causa
5. **Implementar** correções
6. **Reportar** conforme política interna

#### Contatos de Emergência
```
Security Team: security@company.com
CISO: ciso@company.com
Legal: legal@company.com
Emergency: +55 11 9999-9999
```

---

**🔒 Lembre-se: Com grandes poderes vêm grandes responsabilidades.**

> "O JARVIS é uma ferramenta poderosa. Use-o apenas para o bem e sempre dentro da lei."