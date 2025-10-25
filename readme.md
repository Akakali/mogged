# 🎮 Bot de Farm Pokémon - Detector de Skins

Bot automatizado para farm de Pokémon com detecção inteligente de sprites variantes (skins) através de comparação de imagens e OCR.

## ✨ Funcionalidades Principais

### 🎯 Implementadas (Base)
- ✅ **Visualização em Tempo Real**: Janela com bounding boxes coloridas mostrando todas as regiões de detecção
- ✅ **Sistema de Estados Robusto**: Máquina de estados para gerenciar fluxo do bot
- ✅ **Arquitetura Modular**: Código organizado e preparado para expansão
- ✅ **Estatísticas**: Tracking de batalhas, skins encontradas, tempo de execução
- ✅ **Configuração Externa**: Todas as coordenadas e parâmetros em JSON

### 🔧 Para Implementar (TODOs)
- ⏳ **Detecção de Batalha**: Lógica de template matching ou análise de pixels
- ⏳ **OCR**: Extração do nome do Pokémon com pré-processamento
- ⏳ **Comparação de Sprites**: Perceptual hashing (pHash) para detectar diferenças
- ⏳ **Controles**: Envio de comandos de teclado para movimento e fuga
- ⏳ **Sistema de Captura**: Expansão futura para enfraquecer e capturar

## 📁 Estrutura do Projeto

```
bot_pokemon_farm/
├── main.py                 # Orquestrador principal (★ EXECUTAR AQUI)
├── config.json             # Configurações (coordenadas, teclas, parâmetros)
├── requirements.txt        # Dependências Python
├── README.md              # Esta documentação
│
├── assets/
│   └── base_sprites/      # Sprites padrão para comparação
│       ├── mankey.png
│       ├── pidgey.png
│       └── ...
│
├── debug/                 # Screenshots e logs de debug
│   └── (gerado automaticamente)
│
└── modules/
    ├── __init__.py
    ├── screen.py          # Captura de tela e conversões
    ├── detection.py       # OCR, detecção de batalha, comparação
    ├── controls.py        # Input de teclado/mouse
    ├── state_machine.py   # Estados e estatísticas
    └── visualizer.py      # Bounding boxes em tempo real (★ FEATURE PRINCIPAL)
```

## 🚀 Instalação

### 1. Pré-requisitos

**Python 3.8+**
```bash
python --version  # Deve ser 3.8 ou superior
```

**Tesseract-OCR** (necessário para pytesseract)
- **Windows**: [Download aqui](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `sudo apt-get install tesseract-ocr tesseract-ocr-por`
- **macOS**: `brew install tesseract`

### 2. Instalar Dependências

```bash
# Clone ou baixe o projeto
cd bot_pokemon_farm

# Instale as dependências
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Configurar Regiões de Detecção

Abra o jogo e tire um screenshot. Use uma ferramenta como o Paint para descobrir as coordenadas (x, y) de cada região.

Edite `config.json`:

```json
{
  "regions": {
    "battle_indicator": {
      "coords": [100, 50, 200, 100],  // [x1, y1, x2, y2]
      "label": "Battle Indicator",
      "color": [255, 0, 0]  // Vermelho (BGR)
    },
    "pokemon_name": {
      "coords": [50, 150, 250, 200],
      "label": "Pokemon Name",
      "color": [0, 255, 0]  // Verde
    },
    "pokemon_sprite": {
      "coords": [400, 100, 550, 250],
      "label": "Pokemon Sprite",
      "color": [0, 0, 255]  // Azul
    }
  }
}
```

**Dica**: Execute o bot e ajuste as coordenadas até as bounding boxes estarem corretas na janela de visualização!

### 2. Adicionar Sprites Base

Capture screenshots dos sprites **padrão** dos Pokémon que você vai farmar:

1. Encontre o Pokémon padrão no jogo
2. Tire um screenshot da região exata do sprite (use as coordenadas do config)
3. Salve como `assets/base_sprites/nome_pokemon.png`

Exemplo: `assets/base_sprites/mankey.png`

### 3. Configurar Teclas

Ajuste as teclas de controle no `config.json`:

```json
{
  "controls": {
    "move_key_1": "left",   // Tecla para movimento 1
    "move_key_2": "right",  // Tecla para movimento 2
    "flee_key": "z",        // Tecla para fugir
    "interact_key": "x"     // Tecla de interação
  }
}
```

## 🎮 Uso

### Execução Básica

```bash
python main.py
```

### Fluxo de Execução

1. **Inicialização** (5 segundos)
   - Foque na janela do jogo
   - O bot vai iniciar automaticamente

2. **Visualização**
   - Uma janela se abre mostrando a tela do jogo
   - Bounding boxes coloridas indicam cada região de detecção
   - Overlay no topo mostra o estado atual do bot

3. **Farm Loop**
   - O bot se move entre tiles automaticamente
   - Ao detectar batalha, captura e analisa o Pokémon
   - Se for **padrão**: foge e continua farmando
   - Se for **skin**: pausa e alerta você!

4. **Quando Encontrar Skin**
   - Bot pausa automaticamente
   - Screenshot salvo em `debug/`
   - Você assume o controle para capturar

### Atalhos Durante Execução

- `q` ou `ESC`: Fecha a janela de visualização
- `Ctrl+C`: Para o bot e exibe estatísticas

## 🎨 Visualização com Bounding Boxes

### Como Funciona

A **feature principal** deste bot é a visualização em tempo real. Uma janela mostra:

- **Retângulos Coloridos**: Cada região de detecção tem sua cor
  - 🔴 Vermelho: Indicador de batalha
  - 🟢 Verde: Nome do Pokémon
  - 🔵 Azul: Sprite do Pokémon
  - 🟡 Amarelo: UI de batalha

- **Labels**: Texto acima de cada bounding box identificando a região

- **Overlay de Informações**: Painel no topo mostrando:
  - Estado atual do bot
  - Estatísticas (batalhas, skins encontradas)
  - Tempo de execução

### Configuração da Visualização

Em `config.json`:

```json
{
  "visualization": {
    "enabled": true,           // Ativa/desativa visualização
    "bbox_thickness": 2,       // Espessura das linhas
    "font_scale": 0.6,        // Tamanho do texto
    "font_thickness": 2,      // Espessura do texto
    "update_interval": 0.1    // Taxa de atualização (segundos)
  }
}
```

## 🔧 Implementação Pendente

O projeto está estruturado com TODOs bem documentados. Áreas principais para implementar:

### 1. Detecção de Batalha (`modules/detection.py`)

```python
def is_in_battle(self) -> bool:
    # TODO: Implementar detecção
    # Opção 1: Template matching (melhor)
    # Opção 2: Análise de pixels específicos
    # Opção 3: Comparação de frames
```

**Sugestões**:
- Use `cv2.matchTemplate()` com uma imagem da UI de batalha
- Ou conte pixels de uma cor específica na região indicadora

### 2. OCR do Nome (`modules/detection.py`)

```python
def get_pokemon_name(self) -> Optional[str]:
    # TODO: Implementar OCR robusto
    # 1. Pré-processar (grayscale, threshold, resize)
    # 2. Executar pytesseract
    # 3. Limpar resultado com regex
```

**Dicas**:
- Binarize a imagem antes do OCR (threshold)
- Use `--psm 7` no Tesseract para linha única
- Remova "LV.", números e caracteres especiais

### 3. Comparação de Sprites (`modules/detection.py`)

```python
def is_pokemon_skinned(self, pokemon_name: str) -> Tuple[bool, float]:
    # TODO: Implementar perceptual hashing
    # 1. Carregar sprite base
    # 2. Capturar sprite atual
    # 3. Calcular hashes com imagehash.phash()
    # 4. Comparar: diferença > threshold = skin
```

**Método Recomendado**:
```python
import imagehash

base_hash = imagehash.phash(base_sprite)
captured_hash = imagehash.phash(captured_sprite)
difference = base_hash - captured_hash

if difference > 5:  # Threshold ajustável
    return (True, float(difference))  # É skin!
```

### 4. Controles (`modules/controls.py`)

```python
def move_between_tiles(self):
    # TODO: Implementar movimento A-B
    self.press_key('left')
    time.sleep(1)
    self.press_key('right')
    time.sleep(1)
```

### 5. Desenho de Bounding Boxes (`modules/screen.py`)

A estrutura está pronta, apenas descomente o código:

```python
def draw_bounding_boxes(self, base_image):
    # O código está comentado, só descomentar!
    for region_name, region_data in self.regions.items():
        coords = region_data['coords']
        label = region_data['label']
        color = tuple(region_data['color'])
        
        cv2.rectangle(annotated_image, ...)  # Já está lá!
        cv2.putText(annotated_image, ...)    # Já está lá!
```

## 📊 Sistema de Estados

```
     START
       ↓
    [IDLE]
       ↓
   [FARMING] ←──────┐
       ↓             │
  [IN_BATTLE]       │
       ↓             │
    É skin?         │
     /    \          │
   SIM    NÃO       │
    ↓      ↓         │
[PAUSED] [Foge]────┘
    ↓
[STOPPED]
```

## 📈 Estatísticas

O bot rastreia automaticamente:

- ⏱️ Tempo de execução
- 🎮 Total de batalhas
- ✨ Skins encontradas
- 🏃 Fugas realizadas
- ❌ Erros ocorridos
- 📊 Taxa de skin (%)

Exibidas ao encerrar o bot com `Ctrl+C`.

## 🐛 Debug

### Screenshots Automáticos

Quando uma skin é encontrada, o bot salva automaticamente em `debug/`:
```
debug/skin_mankey_1234567890.png
```

### Ferramentas de Debug

```python
# Comparação visual de sprites
from modules.visualizer import DebugVisualizer

DebugVisualizer.show_region_comparison(base_img, captured_img)
DebugVisualizer.show_ocr_preprocessing(original, processed, text_result)
```

### Histórico de Estados

```python
bot.state_machine.print_history(last_n=20)
```

## 🚀 Expansão Futura

### Sistema de Captura Completo

Quando implementar a lógica de batalha, adicione em `data/`:

```json
// team.json
{
  "active_pokemon": {
    "name": "Butterfree",
    "attacks": [
      {
        "slot": 1,
        "name": "Confusion",
        "power": 50,
        "accuracy": 100,
        "type": "Psychic"
      }
    ],
    "level": 25
  }
}
```

E implemente em `modules/battle_logic.py`:
- Cálculo de dano para enfraquecer
- Lógica de captura (% de HP para usar bola)
- Seleção inteligente de ataques

### Padrões de Movimento

```python
# Em modules/controls.py → MovementPattern
def circular_pattern(self, radius=5):
    # Movimento circular para cobrir mais área
    
def random_walk(self, steps=10):
    # Movimento aleatório (mais humano)
```

### Notificações

```python
# Quando encontrar skin
import winsound  # Windows
winsound.Beep(1000, 500)

# Ou Discord webhook
import requests
requests.post(webhook_url, json={"content": "SKIN ENCONTRADA!"})
```

## ⚠️ Avisos Importantes

1. **Uso Responsável**: Este bot é para fins educacionais. Verifique os termos de serviço do jogo.

2. **Tesseract**: Instale o Tesseract-OCR no sistema, não apenas o pytesseract.

3. **Coordenadas**: As coordenadas são específicas da sua resolução. Ajuste no config.json.

4. **Performance**: Se a visualização estiver lenta, aumente `update_interval` no config.

5. **Anti-cheat**: Alguns jogos detectam automação. Use por sua conta e risco.

## 📝 Licença

MIT License - Use, modifique e distribua livremente.

## 🤝 Contribuindo

Pull requests são bem-vindos! Áreas que precisam de ajuda:

- [ ] Implementar detecção de batalha robusta
- [ ] Melhorar OCR com diferentes fontes
- [ ] Adicionar mais métodos de comparação (SSIM, MSE)
- [ ] Criar sistema de profiles para diferentes jogos
- [ ] Adicionar interface gráfica (GUI)

## 📧 Suporte

Se encontrar bugs ou tiver sugestões:
1. Verifique se as coordenadas estão corretas
2. Teste com `debug=True` no config
3. Envie screenshots do `debug/` folder

---

**Desenvolvido com ❤️ para a comunidade Pokémon**

Happy Hunting! ✨🎮