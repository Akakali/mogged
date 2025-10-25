"""
Módulo de Controles - IMPLEMENTADO
===================================
Envio de inputs de teclado para o jogo.
"""

from pynput.keyboard import Key, Controller
import time
from typing import Optional


class GameController:
    """Gerencia todos os inputs enviados para o jogo."""

    def __init__(self, config: dict):
        self.config = config
        self.keyboard = Controller()
        self.controls = config.get('controls', {})
        self.behavior = config.get('bot_behavior', {})

        # Mapeamento de strings para keys do pynput
        self.key_map = {
            'left': Key.left,
            'right': Key.right,
            'up': Key.up,
            'down': Key.down,
            'enter': Key.enter,
            'space': Key.space,
            'esc': Key.esc,
        }

    def press_key(self, key_name: str, duration: float = 0.1) -> None:
        """
        Pressiona uma tecla por um tempo determinado.

        Args:
            key_name: Nome da tecla (ex: 'left', 'z', 'x')
            duration: Tempo que a tecla fica pressionada
        """
        # Converte string para Key object se estiver no mapa
        key = self.key_map.get(key_name, key_name)

        try:
            self.keyboard.press(key)
            time.sleep(duration)
            self.keyboard.release(key)
        except Exception as e:
            print(f"[ERRO] Pressionar tecla '{key_name}': {e}")

    def tap_key(self, key_name: str, times: int = 1, delay: float = 0.1) -> None:
        """
        Toca uma tecla várias vezes rapidamente.

        Args:
            key_name: Nome da tecla
            times: Número de vezes para pressionar
            delay: Delay entre cada pressão
        """
        for i in range(times):
            self.press_key(key_name, duration=0.05)
            if i < times - 1:  # Não aguarda após última tecla
                time.sleep(delay)

    def move_between_tiles(self) -> None:
        """
        Executa o movimento A-B entre os dois tiles de arbusto.

        Movimento básico para farm:
        1. Move para esquerda
        2. Aguarda
        3. Move para direita
        4. Aguarda
        """
        key1 = self.controls.get('move_key_1', 'left')
        key2 = self.controls.get('move_key_2', 'right')
        delay = self.behavior.get('movement_delay', 1.0)

        print(f"[MOVIMENTO] {key1.upper()}", end='')
        self.press_key(key1, duration=0.15)
        time.sleep(delay)

        print(f" → {key2.upper()}")
        self.press_key(key2, duration=0.15)
        time.sleep(delay)

    def flee_battle(self) -> None:
        """
        Executa a sequência de fuga da batalha.

        Sequência genérica de fuga em Pokémon:
        1. Pressiona Z/X para abrir menu
        2. Pressiona para baixo para ir em "Fugir"
        3. Confirma com Z/X

        Ajuste conforme seu jogo específico!
        """
        flee_key = self.controls.get('flee_key', 'z')
        action_delay = self.behavior.get('action_delay', 0.5)

        print(f"[FUGA] Iniciando sequência...")

        # Abre menu de batalha
        self.tap_key(flee_key, times=1)
        time.sleep(action_delay)

        # Navega até "Fugir" (geralmente está embaixo)
        # Ajuste o número de "downs" conforme necessário
        self.press_key('down')
        time.sleep(action_delay * 0.5)

        # Confirma fuga
        self.tap_key(flee_key, times=1)
        time.sleep(action_delay)

        # Confirma novamente se necessário (alguns jogos precisam)
        self.tap_key(flee_key, times=1)

        print(f"[FUGA] Sequência completa")

    def use_pokeball(self, ball_type: str = "pokeball") -> None:
        """
        Usa uma Pokébola para tentar capturar.

        TODO: Implementar quando expandir para captura
        Sequência típica:
        1. Abrir menu de itens/bag
        2. Navegar até a bola
        3. Selecionar
        4. Aguardar animação
        """
        print(f"[CAPTURA] Usando {ball_type}...")
        interact_key = self.controls.get('interact_key', 'x')

        # Placeholder - implementar lógica completa depois
        self.tap_key(interact_key, times=1)

    def select_attack(self, attack_position: int) -> None:
        """
        Seleciona um ataque na batalha (posições 1-4).

        TODO: Implementar quando adicionar lógica de enfraquecer
        """
        print(f"[ATAQUE] Selecionando ataque #{attack_position}")

        # Mapeia posição para teclas
        # Assumindo layout típico: 1=cima-esq, 2=cima-dir, 3=baixo-esq, 4=baixo-dir
        movements = {
            1: [],  # Já selecionado por padrão
            2: ['right'],
            3: ['down'],
            4: ['down', 'right']
        }

        # Navega até o ataque
        for direction in movements.get(attack_position, []):
            self.press_key(direction)
            time.sleep(0.2)

        # Confirma
        self.tap_key(self.controls.get('flee_key', 'z'), times=1)

    def wait(self, seconds: float) -> None:
        """Espera um tempo determinado."""
        time.sleep(seconds)

    def emergency_stop(self) -> None:
        """
        Para todas as ações imediatamente.
        Útil quando detectar uma skin.
        """
        # Libera todas as teclas
        # (pynput libera automaticamente ao usar press/release)
        print("[EMERGÊNCIA] Controles pausados!")


class MovementPattern:
    """
    Padrões de movimento avançados (expansão futura).
    """

    def __init__(self, controller: GameController):
        self.controller = controller

    def circular_pattern(self, radius: int = 5) -> None:
        """
        Movimento em círculo.

        Útil para cobrir uma área maior de farm.
        """
        directions = ['up', 'right', 'down', 'left']

        for _ in range(radius):
            for direction in directions:
                self.controller.press_key(direction)
                self.controller.wait(0.5)

    def random_walk(self, steps: int = 10) -> None:
        """
        Movimento aleatório para parecer mais humano.
        """
        import random
        directions = ['up', 'down', 'left', 'right']

        for _ in range(steps):
            direction = random.choice(directions)
            self.controller.press_key(direction)
            self.controller.wait(random.uniform(0.3, 0.8))

    def follow_path(self, path: list) -> None:
        """
        Segue uma lista de movimentos.

        Args:
            path: ['up', 'right', 'down', 'left', ...]
        """
        for direction in path:
            self.controller.press_key(direction)
            self.controller.wait(0.5)

        print(f"[MOVIMENTO] Caminho completo ({len(path)} passos)")