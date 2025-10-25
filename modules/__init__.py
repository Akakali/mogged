"""
Módulo Bot de Farm Pokémon
===========================

Este pacote contém todos os módulos necessários para o bot de farm.

Módulos:
screen: Captura e processamento de tela
detection: OCR, detecção de batalha e comparação de sprites
controls: Controle de teclado e mouse
state_machine: Gerenciamento de estados e estatísticas
visualizer: Visualização com bounding boxes em tempo real

Versão: 1.0.0
"""

version = "1.0.0"
author = "Pokemon Farm Bot Team"

from .screen import ScreenCapture
from .detection import BattleDetector, PokemonIdentifier, SpriteComparator
from .controls import GameController, MovementPattern
from .state_machine import StateMachine, BotState, BotStatistics
from .visualizer import BoundingBoxVisualizer, DebugVisualizer

all = [
    'ScreenCapture',
    'BattleDetector',
    'PokemonIdentifier',
    'SpriteComparator',
    'GameController',
    'MovementPattern',
    'StateMachine',
    'BotState',
    'BotStatistics',
    'BoundingBoxVisualizer',
    'DebugVisualizer',
]
