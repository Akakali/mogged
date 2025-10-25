"""
BOT DE FARM POKÉMON - DETECTOR DE SKINS
========================================

Bot automatizado para farm de Pokémon com detecção de sprites variantes (skins).

Funcionalidades Principais:
1. Movimento automático entre tiles para encontrar batalhas
2. Detecção de início de batalha
3. OCR para identificar nome do Pokémon
4. Comparação de sprites para detectar skins
5. Visualização em tempo real com bounding boxes
6. Sistema de estados robusto

Autor: [Seu Nome]
Data: 2025
Versão: 1.0.0 (Base Implementation)
"""

import json
import time
import sys
from pathlib import Path

# Imports dos módulos personalizados
from modules.screen import ScreenCapture
from modules.detection import BattleDetector, PokemonIdentifier, SpriteComparator
from modules.controls import GameController
from modules.state_machine import StateMachine, BotState, BotStatistics
from modules.visualizer import BoundingBoxVisualizer


class PokemonFarmBot:
    """
    Classe principal que orquestra todos os módulos do bot.
    """

    def __init__(self, config_path: str = "config.json"):
        """
        Inicializa o bot carregando as configurações.

        Args:
            config_path: Caminho para o arquivo de configuração
        """
        print("=" * 60)
        print("POKÉMON FARM BOT - DETECTOR DE SKINS")
        print("=" * 60)

        # Carrega configurações
        self.config = self._load_config(config_path)

        # Inicializa módulos
        print("\n[INIT] Inicializando módulos...")
        self.screen = ScreenCapture(self.config)
        self.state_machine = StateMachine()
        self.statistics = BotStatistics()
        self.controller = GameController(self.config)

        # Módulos de detecção
        self.battle_detector = BattleDetector(self.config, self.screen)
        self.pokemon_identifier = PokemonIdentifier(self.config, self.screen)
        self.sprite_comparator = SpriteComparator(self.config, self.screen)

        # Visualizador (feature principal solicitada)
        self.visualizer = BoundingBoxVisualizer(
            self.config,
            self.screen,
            self.state_machine
        )

        # Registra callbacks da máquina de estados
        self._register_state_callbacks()

        print("[INIT] Todos os módulos inicializados com sucesso!")

    def _load_config(self, config_path: str) -> dict:
        """
        Carrega o arquivo de configuração JSON.

        Args:
            config_path: Caminho para config.json

        Returns:
            Dicionário com as configurações
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[CONFIG] Configurações carregadas: {config_path}")
            return config
        except FileNotFoundError:
            print(f"[ERRO] Arquivo de configuração não encontrado: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[ERRO] Erro ao parsear JSON: {e}")
            sys.exit(1)

    def _register_state_callbacks(self) -> None:
        """
        Registra funções callback para transições de estado.

        Callbacks são executados automaticamente quando o estado muda.
        Útil para logging, estatísticas e ações específicas.
        """
        # Quando entra em batalha
        self.state_machine.register_callback(
            BotState.FARMING,
            BotState.IN_BATTLE,
            lambda: self.statistics.increment_encounters()
        )

        # Quando encontra uma skin
        self.state_machine.register_callback(
            BotState.IN_BATTLE,
            BotState.PAUSED,
            lambda: self.statistics.increment_skins()
        )

        # Quando foge de uma batalha
        self.state_machine.register_callback(
            BotState.IN_BATTLE,
            BotState.FARMING,
            lambda: self.statistics.increment_fled()
        )

    def start(self) -> None:
        """
        Inicia o bot.

        Fluxo de execução:
        1. Aguarda 5 segundos para usuário focar na janela do jogo
        2. Inicia a visualização com bounding boxes
        3. Transiciona para estado FARMING
        4. Entra no loop principal
        """
        print("\n" + "=" * 60)
        print("INICIANDO BOT")
        print("=" * 60)
        print("\nPor favor, foque na janela do jogo nos próximos 5 segundos...")

        for i in range(5, 0, -1):
            print(f"Iniciando em {i}...", end='\r')
            time.sleep(1)

        print("\n[BOT] Iniciado!                    ")

        # Inicia visualização
        if self.config.get('visualization', {}).get('enabled', True):
            self.visualizer.start()
            print("[VISUALIZAÇÃO] Janela de detecção aberta")

        # Transiciona para estado de farming
        self.state_machine.transition_to(BotState.FARMING, "Bot iniciado pelo usuário")

        try:
            self._main_loop()
        except KeyboardInterrupt:
            print("\n\n[BOT] Interrompido pelo usuário (Ctrl+C)")
            self.stop()
        except Exception as e:
            print(f"\n\n[ERRO] Exceção não tratada: {e}")
            self.statistics.increment_errors()
            self.stop()

    def _main_loop(self) -> None:
        """
        Loop principal do bot.

        Este é o coração do bot. Ele roda continuamente verificando
        o estado atual e executando as ações apropriadas.

        Fluxo por estado:

        FARMING:
            1. Verifica se entrou em batalha
            2. Se sim, transiciona para IN_BATTLE
            3. Se não, continua movimentando

        IN_BATTLE:
            1. Identifica o nome do Pokémon (OCR)
            2. Captura o sprite
            3. Compara com sprite base
            4. Se for skin: pausa e alerta
            5. Se for padrão: foge e volta para FARMING

        PAUSED:
            - Aguarda ação do usuário
        """
        print("\n[LOOP] Entrando no loop principal...")

        while self.state_machine.current_state != BotState.STOPPED:

            # ====== ESTADO: FARMING ======
            if self.state_machine.is_state(BotState.FARMING):
                self._handle_farming_state()

            # ====== ESTADO: IN_BATTLE ======
            elif self.state_machine.is_state(BotState.IN_BATTLE):
                self._handle_battle_state()

            # ====== ESTADO: PAUSED ======
            elif self.state_machine.is_state(BotState.PAUSED):
                self._handle_paused_state()

            # Pequeno delay para não sobrecarregar CPU
            time.sleep(0.1)

    def _handle_farming_state(self) -> None:
        """
        Lógica do estado FARMING.

        TODO: Implementar lógica completa
            1. Verificar se está em batalha
            2. Se sim, transicionar para IN_BATTLE
            3. Se não, executar movimento A-B
        """
        # Verifica se entrou em batalha
        if self.battle_detector.is_in_battle():
            print("\n[BATALHA] Batalha detectada!")
            self.state_machine.transition_to(
                BotState.IN_BATTLE,
                "Batalha iniciada"
            )

            # Aguarda animação de início de batalha
            battle_delay = self.config['bot_behavior']['battle_start_delay']
            time.sleep(battle_delay)
        else:
            # Continua farmando
            self.controller.move_between_tiles()

    def _handle_battle_state(self) -> None:
        """
        Lógica do estado IN_BATTLE.

        Esta é a lógica CORE do bot - onde acontece a mágica!

        TODO: Implementar lógica completa de batalha
            1. Extrair nome do Pokémon (OCR)
            2. Validar se sprite base existe
            3. Comparar sprites
            4. Decidir ação (pausar ou fugir)
        """
        print("\n[BATALHA] Processando batalha...")

        # 1. Identifica o Pokémon
        pokemon_name = self.pokemon_identifier.get_pokemon_name()

        if pokemon_name is None:
            print("[ERRO] Não foi possível identificar o Pokémon")
            self.statistics.increment_errors()
            self.controller.flee_battle()
            self._wait_battle_end()
            self.state_machine.transition_to(BotState.FARMING, "Erro no OCR, retomando farm")
            return

        print(f"[DETECÇÃO] Pokémon identificado: {pokemon_name.upper()}")

        # 2. Compara sprites
        is_skin, difference = self.sprite_comparator.is_pokemon_skinned(pokemon_name)

        if difference < 0:
            print(f"[AVISO] Sprite base não encontrado para '{pokemon_name}'")
            self.controller.flee_battle()
            self._wait_battle_end()
            self.state_machine.transition_to(BotState.FARMING, "Sprite base ausente")
            return

        print(f"[COMPARAÇÃO] Diferença de sprite: {difference:.2f}")

        # 3. Toma decisão
        if is_skin:
            # ★★★ SKIN ENCONTRADA! ★★★
            print("\n" + "=" * 60)
            print(f"★★★ SKIN ENCONTRADA: {pokemon_name.upper()}! ★★★")
            print(f"Diferença detectada: {difference:.2f}")
            print("=" * 60 + "\n")

            # Salva screenshot para registro
            self.visualizer.save_current_frame(f"debug/skin_{pokemon_name}_{int(time.time())}.png")

            # Pausa o bot
            self.state_machine.transition_to(
                BotState.PAUSED,
                f"Skin detectada: {pokemon_name}"
            )

            # TODO: Aqui pode adicionar:
            # - Alarme sonoro
            # - Notificação desktop
            # - Envio de mensagem (Discord, Telegram, etc)

        else:
            # Pokémon padrão, fugir
            print(f"[DECISÃO] Pokémon padrão. Fugindo...")
            self.controller.flee_battle()
            self._wait_battle_end()
            self.state_machine.transition_to(
                BotState.FARMING,
                "Pokémon padrão, retomando farm"
            )

    def _handle_paused_state(self) -> None:
        """
        Lógica do estado PAUSED.

        Quando pausado, o bot aguarda ação do usuário.
        Exibe estatísticas e opções.
        """
        print("\n[PAUSA] Bot pausado. Aguardando ação do usuário...")
        print("Opções:")
        print("  - Pressione 'r' para retomar o farm")
        print("  - Pressione 'q' para encerrar o bot")
        print("  - Pressione 's' para ver estatísticas")

        # TODO: Implementar input do usuário
        # Por enquanto, apenas aguarda
        time.sleep(1)

    def _wait_battle_end(self) -> None:
        """
        Aguarda o fim da batalha atual.

        Monitora a tela até que a UI de batalha desapareça.
        """
        print("[BATALHA] Aguardando fim da batalha...")

        max_wait = 10  # Segundos máximos para aguardar
        elapsed = 0

        while self.battle_detector.is_in_battle() and elapsed < max_wait:
            time.sleep(0.5)
            elapsed += 0.5

        if elapsed >= max_wait:
            print("[AVISO] Timeout aguardando fim de batalha")
        else:
            print("[BATALHA] Batalha finalizada")

    def stop(self) -> None:
        """
        Para o bot gracefully.

        Executa cleanup de todos os módulos e exibe estatísticas finais.
        """
        print("\n[BOT] Encerrando...")

        # Para visualização
        if self.visualizer:
            self.visualizer.stop()

        # Transiciona para STOPPED
        self.state_machine.transition_to(BotState.STOPPED, "Bot encerrado pelo usuário")

        # Exibe estatísticas finais
        self.statistics.print_summary()

        # Exibe histórico de estados
        self.state_machine.print_history(last_n=20)

        print("\n[BOT] Encerrado com sucesso!")
        print("=" * 60)


def main():
    """
    Função principal de entrada do programa.
    """
    # Verifica se todos os diretórios necessários existem
    Path("assets/base_sprites").mkdir(parents=True, exist_ok=True)
    Path("debug").mkdir(parents=True, exist_ok=True)

    # Cria e inicia o bot
    bot = PokemonFarmBot(config_path="config.json")
    bot.start()


if __name__ == "__main__":
    """
    Ponto de entrada quando o script é executado diretamente.

    Uso:
        python main.py
    """
    main()
