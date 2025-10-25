# ✅ CHECKLIST DE IMPLEMENTAÇÃO E USO

## 📦 INSTALAÇÃO (Faça UMA vez)

### 1. Dependências do Sistema
```bash
- [ ] Python 3.8+ instalado
      python --version

- [ ] Tesseract-OCR instalado
      # Windows: https://github.com/UB-Mannheim/tesseract/wiki
      # Linux: sudo apt-get install tesseract-ocr
      # macOS: brew install tesseract
```

### 2. Dependências Python
```bash
- [ ] Instalar pacotes
      pip install -r requirements.txt

- [ ] Verificar instalação
      python -c "import cv2, pytesseract, imagehash; print('✅ OK')"
```

---

## ⚙️ CONFIGURAÇÃO INICIAL

### 3. Estrutura de Diretórios
```bash
- [ ] Criar diretórios necessários
      mkdir -p assets/base_sprites debug
```

### 4. Ajustar Coordenadas
```bash
- [ ] Abrir o jogo em TELA CHEIA ou janela fixa
      (Importante: mantenha sempre a mesma resolução!)

- [ ] Usar Paint/ShareX para encontrar coordenadas
      - battle_indicator: [x1, y1, x2, y2]
      - pokemon_name: [x1, y1, x2, y2]
      - pokemon_sprite: [x1, y1, x2, y2]
      - battle_ui: [x1, y1, x2, y2]

- [ ] Atualizar config.json com as coordenadas

OU usar ferramenta automática:
      python -c "from modules.screen import calibrate_regions; calibrate_regions()"
```

### 5. Capturar Sprites Base
```bash
- [ ] Entrar em batalha com Pokémon PADRÃO (sem skin)

- [ ] Capturar sprites:
      # Modo interativo:
      python capture_sprites.py
      
      # Modo rápido (1 sprite):
      python capture_sprites.py pikachu

- [ ] Verificar se salvou corretamente:
      python capture_sprites.py  # Opção 3 (listar)

- [ ] Mínimo 1 sprite para testar
      Recomendado: 5-10 sprites dos Pokémon comuns da área
```

---

## 🧪 TESTES (CRÍTICO - Não pule!)

### 6. Validar Captura de Tela
```bash
- [ ] Executar teste:
      python test_modules.py  # Opção 1

- [ ] Verificar imagens salvas em debug/
      - Todas as regiões devem estar corretas
      - Se não: ajustar config.json e repetir

- [ ] ✅ PASSOU: coordenadas corretas
      ❌ FALHOU: ajustar coordenadas
```

### 7. Validar Visualização
```bash
- [ ] Executar teste:
      python test_modules.py  # Opção 2

- [ ] Verificar janela que abre:
      - Bounding boxes devem estar sobre as regiões corretas
      - Labels devem estar visíveis
      - Não pode estar cortado/fora da tela

- [ ] ✅ PASSOU: boxes estão corretas
      ❌ FALHOU: ajustar coordenadas
```

### 8. Validar Detecção de Batalha
```bash
- [ ] Executar teste:
      python test_modules.py  # Opção 3

- [ ] Durante o teste:
      - Iniciar uma batalha no jogo
      - Deve detectar e mostrar "🔴 BATALHA"
      - Ao sair da batalha, deve mostrar "🟢 Farm"

- [ ] ✅ PASSOU: detecta corretamente
      ❌ FALHOU: ajustar região battle_indicator
```

### 9. Validar OCR
```bash
- [ ] Entrar em batalha ANTES de executar

- [ ] Executar teste:
      python test_modules.py  # Opção 4

- [ ] Verificar se nome foi extraído:
      - Nome deve estar correto e em lowercase
      - Ex: "PIKACHU" → "pikachu"

- [ ] ✅ PASSOU: nome correto
      ❌ FALHOU: 
        - Tesseract não instalado?
        - Coordenadas pokemon_name erradas?
        - Fonte do jogo não suportada? (aumentar região)
```

### 10. Validar Comparação de Sprites
```bash
- [ ] Ter pelo menos 1 sprite base capturado

- [ ] Entrar em batalha com o MESMO Pokémon (padrão)

- [ ] Executar teste:
      python test_modules.py  # Opção 5

- [ ] Verificar resultado:
      - Difference deve ser BAIXA (0-3)
      - "É skin? NÃO"
      - Verificar debug/comparison_*.png

- [ ] (Opcional) Testar com sprite diferente:
      - Entrar em batalha com Pokémon DIFERENTE
      - Repetir teste
      - Difference deve ser ALTA (>10)

- [ ] ✅ PASSOU: detecta diferenças
      ❌ FALHOU:
        - Sprite base está correto?
        - Ajustar hash_threshold no config
```

### 11. Validar Controles
```bash
- [ ] Focar na janela do jogo

- [ ] Executar teste:
      python test_modules.py  # Opção 6

- [ ] Verificar se os comandos foram enviados:
      - Personagem deve se mover (esquerda/direita)
      - Se em batalha, deve tentar fugir

- [ ] ✅ PASSOU: comandos funcionam
      ❌ FALHOU:
        - Teclas corretas no config?
        - Jogo não está com foco?
```

### 12. (Recomendado) Executar TODOS os Testes
```bash
- [ ] Executar suite completa:
      python test_modules.py  # Opção 7

- [ ] Acompanhar cada teste e seguir instruções

- [ ] Verificar resumo final:
      Todos devem passar antes de usar o bot!
```

---

## 🚀 PRIMEIRA EXECUÇÃO

### 13. Preparar o Jogo
```bash
- [ ] Posicionar personagem em área de farm
      - Deve ter 2 tiles de grama adjacentes
      - Área com Pokémon que você quer farmar

- [ ] Salvar o jogo (segurança!)

- [ ] Deixar jogo em primeiro plano

- [ ] (Opcional) Reduzir velocidade de texto/animações
```

### 14. Executar o Bot
```bash
- [ ] Iniciar bot:
      python main.py

- [ ] Aguardar 5 segundos (foque na janela do jogo)

- [ ] Verificar se:
      - Janela de visualização abriu
      - Bot está no estado "FARMING"
      - Personagem está se movendo
      - Detecta batalhas quando ocorrem

- [ ] Deixar rodando por 5-10 minutos (teste inicial)
```

### 15. Monitorar Execução
```bash
Durante a execução, observe:

- [ ] Terminal mostra logs:
      [MOVIMENTO] LEFT → RIGHT
      [BATALHA] Batalha detectada!
      [OCR] Nome detectado: 'pidgey'
      [COMPARAÇÃO] Hash diff: 2.0
      [FUGA] Iniciando sequência...

- [ ] Janela mostra:
      - Estado atual (FARMING / IN_BATTLE)
      - FPS (~5-15 fps é normal)
      - Estatísticas atualizando

- [ ] Jogo responde aos comandos:
      - Movimento funciona
      - Fuga funciona
      - Batalhas são detectadas
```

---

## 🎯 QUANDO ENCONTRAR UMA SKIN

### 16. Ação Automática do Bot
```bash
Quando skin é detectada:

- [ ] Bot PAUSA automaticamente
      Estado muda para "PAUSED"

- [ ] Terminal mostra:
      ★★★ SKIN ENCONTRADA: PIKACHU! ★★★
      Diferença detectada: 8.50

- [ ] Screenshot é salvo:
      debug/skin_pikachu_<timestamp>.png

- [ ] Você assume o controle!
```

### 17. Suas Ações
```bash
- [ ] Verificar se realmente é skin:
      - Olhar o jogo
      - Conferir screenshot salvo

- [ ] Se for skin REAL:
      - Capturar o Pokémon manualmente
      - Salvar o jogo

- [ ] Se for FALSO POSITIVO:
      - Anotar o Pokémon
      - Ajustar hash_threshold depois
      - Fugir manualmente

- [ ] Parar o bot (Ctrl+C) ou retomar farm
```

---

## 🔧 AJUSTES PÓS-TESTE

### 18. Problemas Comuns e Soluções

**❌ Muitos Falsos Positivos (detecta skin quando não é)**
```bash
- [ ] SOLUÇÃO: Aumentar threshold
      config.json → "hash_threshold": 8  (era 5)
      
- [ ] Recapturar sprite base
      - Deve ser do jogo, não de wiki
      - Mesma resolução e ângulo
```

**❌ Não Detecta Skins Reais**
```bash
- [ ] SOLUÇÃO: Diminuir threshold
      config.json → "hash_threshold": 3  (era 5)
      
- [ ] Ativar confirmação SSIM (mais preciso):
      config.json → "use_ssim_confirmation": true
```

**❌ Não Detecta Batalhas**
```bash
- [ ] SOLUÇÃO 1: Ajustar região
      Aumentar área de battle_indicator
      
- [ ] SOLUÇÃO 2: Ajustar sensibilidade
      Em modules/detection.py linha ~35:
      is_battle = white_percentage > 15  (era 20)
```

**❌ OCR Sempre Falha**
```bash
- [ ] SOLUÇÃO 1: Aumentar região
      pokemon_name deve pegar TODO o texto
      
- [ ] SOLUÇÃO 2: Mudar PSM do Tesseract
      Em modules/detection.py linha ~68:
      self.tesseract_config = '--psm 6 --oem 3'
      
- [ ] SOLUÇÃO 3: Usar fonte alternativa
      Alguns jogos têm fontes difíceis
      Considere usar template matching em vez de OCR
```

**❌ Bot Não Move/Foge**
```bash
- [ ] SOLUÇÃO: Ajustar delays
      config.json → bot_behavior:
      "movement_delay": 1.5  (era 1.0)
      "action_delay": 0.8    (era 0.5)
      
- [ ] Verificar teclas corretas
      Testar manualmente no jogo
```

---

## 📊 OTIMIZAÇÃO

### 19. Performance
```bash
- [ ] Se visualização está lenta:
      config.json → visualization:
      "update_interval": 0.2  (era 0.1)
      
- [ ] Se bot está pesado:
      - Fechar programas em background
      - Reduzir resolução do jogo
      - Desabilitar visualização (debug)
```

### 20. Precisão
```bash
- [ ] Capturar sprites de TODOS os Pokémon da área
      Quanto mais sprites, melhor a detecção
      
- [ ] Testar com cada Pokémon:
      - Entrar em batalha
      - Verificar hash difference
      - Anotar valores típicos
      
- [ ] Ajustar threshold baseado nos dados:
      Se diferenças padrão = 0-3
      E diferenças skin = 8-15
      Então threshold ideal = 5-6
```

---

## 📈 MONITORAMENTO A LONGO PRAZO

### 21. Durante Farm Prolongado
```bash
A cada 30 minutos, verificar:

- [ ] Estatísticas estão razoáveis?
      - Taxa de skin: 1-5% é normal
      - Erros: deve ser próximo de 0
      - Batalhas: deve aumentar consistentemente
      
- [ ] Bot ainda está funcionando?
      - Não travou em batalha
      - Ainda está se movendo
      - Visualização atualizando
      
- [ ] Jogo não crashou/bugou?
      - Personagem não está preso
      - Não entrou em diálogo/menu
```

### 22. Ao Encerrar (Ctrl+C)
```bash
- [ ] Verificar estatísticas finais:
      ⏱️  Tempo de execução
      🎮 Total de batalhas
      ✨ Skins encontradas
      🏃 Fugas realizadas
      ❌ Erros
      📊 Taxa de skin (%)
      
- [ ] Salvar o jogo manualmente
      
- [ ] Backup dos screenshots importantes:
      debug/skin_*.png
```

---

## 🚀 EXPANSÕES FUTURAS

### 23. Próximos Passos (Opcional)
```bash
- [ ] Implementar sistema de captura
      - Lógica de enfraquecer (cálculo de dano)
      - Escolha inteligente de Pokébola
      
- [ ] Adicionar notificações
      - Som de alerta (winsound)
      - Discord webhook
      - E-mail/SMS
      
- [ ] Melhorar movimentação
      - Padrão circular
      - Movimento aleatório (mais humano)
      - Rotas específicas
      
- [ ] Criar GUI
      - PyQt5/Tkinter
      - Configuração visual
      - Gráficos de estatísticas
      
- [ ] Machine Learning
      - Treinar modelo CNN para detectar skins
      - Detecção de batalha mais robusta
      - OCR próprio (sem Tesseract)
```

---

## ⚠️ SEGURANÇA E BOAS PRÁTICAS

### 24. Antes de Usar
```bash
- [ ] Ler termos de serviço do jogo
      Automação pode ser contra as regras
      
- [ ] Usar em conta secundária (recomendado)
      Para testes e aprendizado
      
- [ ] Salvar o jogo frequentemente
      Bot pode ter bugs
      
- [ ] Não deixar sem supervisão por horas
      Monitorar periodicamente
```

### 25. Ética
```bash
- [ ] Uso educacional e pessoal
      Aprender sobre automação, CV, OCR
      
- [ ] Não vender/distribuir skins farmadas
      Pode prejudicar economia do jogo
      
- [ ] Respeitar outros jogadores
      Não usar em PvP ou trading
```

---

## 📝 REGISTRO DE PROGRESSO

### Anote seus resultados:

**Data: ___/___/___**

**Configuração:**
- Resolução do jogo: _________
- Área de farm: _________
- Pokémon alvo: _________
- Hash threshold: _________

**Resultados:**
- Tempo total: ___ horas
- Batalhas: _________
- Skins encontradas: _________
- Taxa de skin: _________%
- Falsos positivos: _________

**Observações:**
_________________________________
_________________________________
_________________________________

---

## ✅ CHECKLIST FINAL

Antes de considerar implementação completa:

- [ ] Todos os testes passam (1-12)
- [ ] Bot funciona por 30+ minutos sem erros
- [ ] Detecta batalhas corretamente (>95%)
- [ ] OCR funciona (>80% acerto)
- [ ] Comparação de sprites precisa
- [ ] Pelo menos 1 skin real detectada e confirmada
- [ ] Falsos positivos < 5%
- [ ] Controles funcionam perfeitamente
- [ ] Visualização estável
- [ ] Documentação lida e compreendida

**SE TODOS MARCADOS: 🎉 Bot está pronto para uso!**

---

**Desenvolvido com ❤️ para a comunidade Pokémon**

*Happy Hunting! ✨🎮*