"""
Módulo de Controles
===================
Responsável por enviar inputs de teclado/mouse para o jogo.

Funcionalidades:
- Envio de comandos de teclado
- Sequências de movimento
- Ações de batalha (fugir, atacar)
"""

from pynput.keyboard import Key, Controller
import time
from typing import Optional


class GameController:
    """
    Gerencia todos os inputs enviados para o jogo.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: Configurações do bot
        """
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
            duration: Tempo que a tecla fica pressionada (segundos)

        Example:
            >>> controller.press_key('left', 0.2)
            >>> controller.press_key('z', 0.1)
        """
        # Converte string para Key object se estiver no mapa
        key = self.key_map.get(key_name, key_name)

        self.keyboard.press(key)
        time.sleep(duration)
        self.keyboard.release(key)

    def tap_key(self, key_name: str, times: int = 1, delay: float = 0.1) -> None:
        """
        Toca uma tecla várias vezes rapidamente.

        Args:
            key_name: Nome da tecla
            times: Número de vezes para pressionar
            delay: Delay entre cada pressão

        Example:
            >>> controller.tap_key('x', times=3)  # Confirma 3 vezes
        """
        for _ in range(times):
            self.press_key(key_name, duration=0.05)
            time.sleep(delay)

    def move_between_tiles(self) -> None:
        """
        Executa o movimento A-B entre os dois tiles de arbusto.

        Esta é a lógica principal de farm. O bot fica alternando entre
        dois tiles para encontrar encontros aleatórios.

        TODO: Implementar padrão de movimento
            1. Pressionar move_key_1 (ex: esquerda)
            2. Esperar movement_delay
            3. Pressionar move_key_2 (ex: direita)
            4. Esperar movement_delay

        Movimento pode ser customizado no futuro:
            - Circular: up -> right -> down -> left
            - Aleatório: escolha randômica de direção
            - Padrão específico: seguir uma lista de movimentos
        """
        key1 = self.controls.get('move_key_1', 'left')
        key2 = self.controls.get('move_key_2', 'right')
        delay = self.behavior.get('movement_delay', 1.0)

        # TODO: Implementar movimento
        # self.press_key(key1)
        # time.sleep(delay)
        # self.press_key(key2)
        # time.sleep(delay)

        print(f"[MOVIMENTO] {key1} -> {key2}")
        time.sleep(delay * 2)

    def flee_battle(self) -> None:
        """
        Executa a sequência de fuga da batalha.

        TODO: Implementar sequência de fuga
            Geralmente em Pokémon:
            1. Abrir menu (tap 'z' ou 'x')
            2. Navegar até "Fugir" (setas)
            3. Confirmar (tap 'z' ou 'x')

        A sequência exata depende do jogo.
        Pode precisar de múltiplos taps e delays.
        """
        flee_key = self.controls.get('flee_key', 'z')
        action_delay = self.behavior.get('action_delay', 0.5)

        # TODO: Implementar sequência correta
        # Exemplo genérico:
        # self.tap_key(flee_key, times=1)
        # time.sleep(action_delay)
        # self.press_key('down')  # Navega até Fugir
        # time.sleep(action_delay)
        # self.tap_key(flee_key, times=1)  # Confirma

        print(f"[FUGA] Usando tecla '{flee_key}'")
        time.sleep(action_delay)

    def use_pokeball(self, ball_type: str = "pokeball") -> None:
        """
        Usa uma Pokébola para tentar capturar.

        Args:
            ball_type: Tipo de bola ("pokeball", "greatball", "ultraball")

        TODO: Implementar uso de Pokébola
            1. Abrir menu de bag
            2. Navegar até a bola correta
            3. Usar
            4. Esperar animação de captura
        """
        print(f"[CAPTURA] Usando {ball_type}")
        # Implementação futura quando expandir para captura
        pass

    def select_attack(self, attack_position: int) -> None:
        """
        Seleciona um ataque na batalha.

        Args:
            attack_position: Posição do ataque (1-4)

        TODO: Implementar seleção de ataque
            1. Confirmar menu de luta (se necessário)
            2. Navegar até posição do ataque
            3. Confirmar

        Será útil quando implementar a lógica de enfraquecer o Pokémon.
        """
        print(f"[ATAQUE] Selecionando ataque na posição {attack_position}")
        # Implementação futura para sistema de batalha completo
        pass

    def wait(self, seconds: float) -> None:
        """
        Espera um tempo determinado. Útil para sincronização.

        Args:
            seconds: Tempo de espera em segundos
        """
        time.sleep(seconds)

    def emergency_stop(self) -> None:
        """
        Para todas as ações imediatamente.
        Útil para quando detectar uma skin e precisar pausar.
        """
        # Libera todas as teclas que possam estar pressionadas
        # (implementação depende do estado do controller)
        print("[EMERGÊNCIA] Bot pausado!")


class MovementPattern:
    """
    Define padrões de movimento mais complexos para expansão futura.
    """

    def __init__(self, controller: GameController):
        """
        Args:
            controller: Instância de GameController
        """
        self.controller = controller

    def circular_pattern(self, radius: int = 5) -> None:
        """
        Movimento em círculo para cobrir área maior.

        TODO: Implementar quando necessário
        """
        pass

    def random_walk(self, steps: int = 10) -> None:
        """
        Movimento aleatório para simular comportamento humano.

        TODO: Implementar quando necessário
        """
        pass

    def follow_path(self, path: list) -> None:
        """
        Segue uma lista de movimentos pré-definida.

        Args:
            path: Lista de direções ['up', 'right', 'down', 'left']

        TODO: Implementar quando necessário para rotas específicas
        """
        pass
