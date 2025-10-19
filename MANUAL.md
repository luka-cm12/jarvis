# Manual do Usuário - JARVIS

Guia completo para usar seu assistente pessoal inteligente JARVIS.

## 🎙️ Comandos de Voz

### Ativação
- **Wake Word:** "Jarvis" ou "Hey Jarvis"
- O LED/status indicará quando JARVIS estiver ouvindo
- Fale normalmente após a confirmação sonora

### Comandos Básicos

#### Saudações e Interação
```
"Jarvis, olá"
"Como você está?"
"Bom dia, JARVIS"
"Boa noite"
"Obrigado"
"Tchau"
```

#### Informações Básicas
```
"Que horas são?"
"Que dia é hoje?"
"Qual a data?"
"Como está o clima?"
"Qual a temperatura?"
```

### Controle de Dispositivos

#### Iluminação
```
"Acenda as luzes"
"Apague as luzes da sala"
"Ligue a luz do quarto"
"Desligue todas as luzes"
"Diminua a intensidade das luzes"
```

#### Clima e Temperatura
```
"Ajuste a temperatura para 22 graus"
"Ligue o ar condicionado"
"Está muito quente aqui"
"Aumente a temperatura"
```

#### Música e Entretenimento
```
"Toque música relaxante"
"Pare a música"
"Aumente o volume"
"Toque minha playlist favorita"
"Coloque jazz"
```

### Automação e Rotinas

#### Criar Rotinas
```
"Crie uma rotina 'bom dia'"
"Configure modo cinema"
"Ative o modo econômia"
"Prepare a casa para dormir"
```

#### Lembretes e Alarmes
```
"Me lembre de tomar remédio às 18h"
"Configure alarme para 7 da manhã"
"Qual meu próximo compromisso?"
"Cancele o alarme"
```

## 🌐 Interface Web

### Acesso
- Abra navegador em: `http://localhost:5000`
- Para acesso remoto: `http://IP-DO-PC:5000`

### Funcionalidades

#### Dashboard Principal
- **Status do Sistema:** Online/Offline
- **Comandos Rápidos:** Envie texto diretamente
- **Controle de Dispositivos:** Botões para ligar/desligar
- **Log em Tempo Real:** Visualize interações

#### Controles Disponíveis
- ✅ Envio de comandos por texto
- ✅ Controle de luzes por ambiente
- ✅ Ajuste de temperatura
- ✅ Visualização de histórico
- ✅ Status dos dispositivos

## 🏠 Integração com Smart Home

### Dispositivos Suportados

#### Philips Hue
- Controle total de lâmpadas e strips
- Ajuste de cor e intensidade
- Grupos e cenas personalizadas

#### Home Assistant
- Integração completa com HA
- Todos os dispositivos conectados
- Automações existentes

#### Sensores e Outros
- Sensores de movimento
- Termostatos inteligentes
- Câmeras de segurança
- Fechaduras inteligentes

### Comandos por Categoria

#### Segurança
```
"Arme o sistema de segurança"
"Desarme o alarme"
"Mostre as câmeras"
"Tranque todas as portas"
"Há alguém na porta?"
```

#### Energia
```
"Ative modo economia"
"Desligue dispositivos não essenciais"
"Quanto estou gastando de energia?"
"Otimize o consumo"
```

## 🧠 Funcionalidades de IA

### Aprendizado Contínuo
- JARVIS aprende suas preferências automaticamente
- Adapta respostas ao seu estilo
- Sugere ações baseadas em padrões
- Melhora com o tempo de uso

### Contexto e Personalização
- Reconhece horários preferidos
- Lembra configurações anteriores
- Adapta-se à rotina diária
- Personaliza saudações e despedidas

### Comandos Inteligentes
```
"Configure como eu gosto"
"Use minhas preferências usuais"
"Faça como ontem"
"Repita a rotina da manhã"
```

## 📱 Uso Mobile

### Acesso via Smartphone
1. Conecte à mesma rede WiFi
2. Abra navegador mobile
3. Acesse IP do computador: `http://192.168.1.X:5000`
4. Interface adaptará para mobile

### Comandos via Celular
- Digite comandos diretamente
- Controle dispositivos por botões
- Visualize status em tempo real
- Receba notificações de eventos

## ⚙️ Configurações Avançadas

### Personalização de Voz

#### Ajustar Velocidade
```json
"voice_settings": {
  "rate": 180    // 50-300 (padrão: 180)
}
```

#### Ajustar Volume
```json
"voice_settings": {
  "volume": 0.8  // 0.0-1.0 (padrão: 0.8)
}
```

### Configurar Personalidade

#### Tom de Voz
- `"professional"` - Formal e elegante
- `"casual"` - Descontraído e amigável
- `"technical"` - Focado em precisão

#### Estilo de Resposta
- `"concise"` - Respostas curtas
- `"detailed"` - Explicações completas
- `"witty"` - Com humor sutil

### Wake Words Personalizados
```json
"jarvis": {
  "wake_word": "computer",     // Personalizar palavra de ativação
  "response_timeout": 5        // Tempo limite para resposta
}
```

## 🔧 Resolução de Problemas

### JARVIS Não Responde
1. Verificar se microfone está funcionando
2. Confirmar palavra de ativação correta
3. Verificar volume do microfone
4. Reiniciar aplicação

### Comandos Não Reconhecidos
- Fale mais devagar e claramente
- Use palavras-chave específicas
- Verifique se comando está na lista suportada
- Treine com variações do comando

### Dispositivos Não Respondem
1. Verificar conexão de rede
2. Confirmar configuração das APIs
3. Testar dispositivos diretamente
4. Verificar logs de erro

### Performance Lenta
- Verificar conexão com internet
- Reduzir `max_tokens` na configuração IA
- Limpar histórico de conversas antigas
- Fechar outros aplicativos pesados

## 📊 Monitoramento e Logs

### Visualizar Atividade
- Interface web mostra log em tempo real
- Arquivo de log: `logs/jarvis.log`
- Histórico de comandos e respostas

### Estatísticas de Uso
- Comandos mais utilizados
- Horários de maior atividade
- Dispositivos mais controlados
- Taxa de sucesso de comandos

### Backup de Dados
- Configurações: `config/config.json`
- Dados de aprendizado: `data/jarvis.db`
- Logs: `logs/jarvis.log`

## 🚀 Dicas de Uso Avançado

### Comandos Compostos
```
"Jarvis, configure modo filme: apague as luzes, feche as cortinas e ligue a TV"
"Modo trabalho: acenda as luzes do escritório, toque música instrumental e ajuste temperatura para 22 graus"
```

### Automações por Horário
- Configure rotinas que executam automaticamente
- JARVIS aprende seus horários preferenciais
- Sugestões proativas baseadas no contexto

### Integração com Calendário
```
"Qual meu próximo compromisso?"
"Me lembre da reunião em 30 minutos"
"Configure alarme 10 minutos antes do evento"
```

### Controle por Contexto
```
"Estou saindo" → Desliga luzes, arma segurança, ajusta termostato
"Chegando em casa" → Liga luzes, desarma alarme, ajusta clima
"Indo dormir" → Rotina noturna completa
```

## 🎯 Casos de Uso Práticos

### Manhã
1. "Bom dia, JARVIS"
2. "Como está o clima hoje?"
3. "Acenda as luzes gradualmente"
4. "Toque notícias do dia"

### Trabalho em Casa
1. "Modo produtivo"
2. "Ajuste a luz para trabalho"
3. "Não me interrompa por 2 horas"
4. "Toque música para concentração"

### Entretenimento
1. "Modo cinema"
2. "Diminua todas as luzes"
3. "Aumente volume do som"
4. "Não atender chamadas"

### Noite
1. "Preparar para dormir"
2. "Tranque todas as portas"
3. "Apague luzes gradualmente"
4. "Configure alarme para amanhã"

---

## 🎓 Treinamento de Voz

Para melhor reconhecimento:
1. Fale com clareza e velocidade normal
2. Mantenha distância de 30-60cm do microfone
3. Evite ruídos de fundo
4. Use comandos consistentes
5. Aguarde confirmação antes do próximo comando

**Lembre-se:** JARVIS fica mais inteligente com o uso!

## 📞 Suporte e Comunidade

- 📧 Email: suporte@jarvis-ai.com
- 🌐 Site: https://jarvis-ai.com
- 💬 Discord: JARVIS Community
- 📖 Wiki: https://wiki.jarvis-ai.com

---

*"Sometimes you gotta run before you can walk."* - Tony Stark