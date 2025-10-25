"""
Módulo de Máquina de Estados
=============================
Gerencia os estados do bot e transições entre eles.

Estados:
- IDLE: Bot iniciado mas não ativo
- FARMING: Movimentando entre tiles procurando batalhas
- IN_BATTLE: Em batalha, processando Pokémon
- CAPTURING: Tentando capturar (futuro)
- PAUSED: Bot pausado (skin encontrada ou erro)
- STOPPED: Bot encerrado
"""

from enum import Enum
from typing import Optional, Callable
from datetime import datetime


class BotState(Enum):
    """
    Estados possíveis do bot.
    """
    IDLE = "idle"  # Bot iniciado, aguardando comando
    FARMING = "farming"  # Farmando (movimento A-B)
    IN_BATTLE = "in_battle"  # Processando batalha
    CAPTURING = "capturing"  # Tentando capturar (futuro)
    PAUSED = "paused"  # Pausado (skin encontrada)
    STOPPED = "stopped"  # Bot encerrado


class StateMachine:
    """
    Gerencia o estado atual do bot e as transições válidas.
    """

    def __init__(self):
        """
        Inicializa a máquina de estados.
        """
        self.current_state = BotState.IDLE
        self.previous_state = None
        self.state_history = []
        self.transition_callbacks = {}

        # Transições válidas: {estado_origem: [estados_destino_válidos]}
        self.valid_transitions = {
            BotState.IDLE: [BotState.FARMING, BotState.STOPPED],
            BotState.FARMING: [BotState.IN_BATTLE, BotState.PAUSED, BotState.STOPPED],
            BotState.IN_BATTLE: [BotState.FARMING, BotState.CAPTURING, BotState.PAUSED, BotState.STOPPED],
            BotState.CAPTURING: [BotState.FARMING, BotState.PAUSED, BotState.STOPPED],
            BotState.PAUSED: [BotState.FARMING, BotState.STOPPED],
            BotState.STOPPED: []  # Estado final
        }

    def transition_to(self, new_state: BotState, reason: str = "") -> bool:
        """
        Transiciona para um novo estado.

        Args:
            new_state: Estado de destino
            reason: Motivo da transição (para logging)

        Returns:
            True se a transição foi bem sucedida, False se inválida

        Example:
            >>> sm = StateMachine()
            >>> sm.transition_to(BotState.FARMING, "Bot iniciado")
            >>> sm.current_state
            <BotState.FARMING: 'farming'>
        """
        # Verifica se a transição é válida
        if new_state not in self.valid_transitions.get(self.current_state, []):
            print(f"[ESTADO] Transição inválida: {self.current_state.value} -> {new_state.value}")
            return False

        # Salva estado anterior
        self.previous_state = self.current_state

        # Registra no histórico
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.state_history.append({
            'timestamp': timestamp,
            'from': self.current_state.value,
            'to': new_state.value,
            'reason': reason
        })

        # Executa callback se registrado
        callback_key = f"{self.current_state.value}_to_{new_state.value}"
        if callback_key in self.transition_callbacks:
            self.transition_callbacks[callback_key]()

        # Atualiza estado
        self.current_state = new_state

        print(f"[ESTADO] {self.previous_state.value} -> {new_state.value} | {reason}")
        return True

    def register_callback(self, from_state: BotState, to_state: BotState,
                          callback: Callable) -> None:
        """
        Registra uma função para ser executada em uma transição específica.

        Args:
            from_state: Estado de origem
            to_state: Estado de destino
            callback: Função a ser executada

        Example:
            >>> def on_battle_start():
            ...     print("Batalha iniciada!")
            >>> sm.register_callback(BotState.FARMING, BotState.IN_BATTLE, on_battle_start)
        """
        callback_key = f"{from_state.value}_to_{to_state.value}"
        self.transition_callbacks[callback_key] = callback

    def is_state(self, state: BotState) -> bool:
        """
        Verifica se o estado atual é o especificado.

        Args:
            state: Estado para verificar

        Returns:
            True se for o estado atual
        """
        return self.current_state == state

    def can_transition_to(self, state: BotState) -> bool:
        """
        Verifica se é possível transicionar para um estado.

        Args:
            state: Estado de destino

        Returns:
            True se a transição for válida
        """
        return state in self.valid_transitions.get(self.current_state, [])

    def get_state_name(self) -> str:
        """
        Retorna o nome do estado atual.

        Returns:
            Nome do estado em string
        """
        return self.current_state.value

    def print_history(self, last_n: int = 10) -> None:
        """
        Imprime o histórico de transições.

        Args:
            last_n: Número de últimas transições para mostrar
        """
        print(f"\n[HISTÓRICO] Últimas {last_n} transições:")
        for entry in self.state_history[-last_n:]:
            print(f"  {entry['timestamp']} | {entry['from']} -> {entry['to']} | {entry['reason']}")

    def reset(self) -> None:
        """
        Reseta a máquina de estados para IDLE.
        """
        self.current_state = BotState.IDLE
        self.previous_state = None
        print("[ESTADO] Máquina de estados resetada")


class BotStatistics:
    """
    Mantém estatísticas do bot durante a execução.
    """

    def __init__(self):
        """
        Inicializa as estatísticas.
        """
        self.start_time = datetime.now()
        self.encounters = 0  # Total de batalhas
        self.skins_found = 0  # Skins encontradas
        self.fled_battles = 0  # Fugas realizadas
        self.captures_attempted = 0  # Tentativas de captura (futuro)
        self.captures_success = 0  # Capturas bem sucedidas (futuro)
        self.errors = 0  # Erros encontrados

    def increment_encounters(self) -> None:
        """Incrementa contador de batalhas."""
        self.encounters += 1

    def increment_skins(self) -> None:
        """Incrementa contador de skins encontradas."""
        self.skins_found += 1

    def increment_fled(self) -> None:
        """Incrementa contador de fugas."""
        self.fled_battles += 1

    def increment_errors(self) -> None:
        """Incrementa contador de erros."""
        self.errors += 1

    def get_runtime(self) -> str:
        """
        Retorna o tempo de execução formatado.

        Returns:
            String formatada (ex: "01:23:45")
        """
        elapsed = datetime.now() - self.start_time
        hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def print_summary(self) -> None:
        """
        Imprime um resumo das estatísticas.
        """
        print("\n" + "=" * 50)
        print("ESTATÍSTICAS DO BOT")
        print("=" * 50)
        print(f"Tempo de execução: {self.get_runtime()}")
        print(f"Batalhas totais:   {self.encounters}")
        print(f"Skins encontradas: {self.skins_found}")
        print(f"Fugas realizadas:  {self.fled_battles}")
        print(f"Erros:             {self.errors}")
        if self.encounters > 0:
            rate = (self.skins_found / self.encounters) * 100
            print(f"Taxa de skin:      {rate:.2f}%")
        print("=" * 50 + "\n")
