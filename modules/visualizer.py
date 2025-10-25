"""
Módulo de Visualização
=======================
Responsável por exibir a tela com bounding boxes em tempo real.

Funcionalidades:
- Desenho de bounding boxes coloridas
- Labels identificando cada região
- Atualização em tempo real
- Overlay de informações do bot
"""

import cv2
import numpy as np
from typing import Optional, Dict, Tuple
import threading
import time


class BoundingBoxVisualizer:
    """
    Gerencia a visualização das bounding boxes em tempo real.

    Esta classe é o CORE da feature solicitada. Ela cria uma janela
    que mostra a tela do jogo com retângulos coloridos e labels em
    cada região de detecção.
    """

    def __init__(self, config: dict, screen_capture, state_machine=None):
        """
        Args:
            config: Configurações do bot
            screen_capture: Instância de ScreenCapture
            state_machine: Instância de StateMachine (opcional)
        """
        self.config = config
        self.screen = screen_capture
        self.state_machine = state_machine

        self.regions = config.get('regions', {})
        self.viz_config = config.get('visualization', {})

        # Configurações de visualização
        self.enabled = self.viz_config.get('enabled', True)
        self.thickness = self.viz_config.get('bbox_thickness', 2)
        self.font_scale = self.viz_config.get('font_scale', 0.6)
        self.font_thickness = self.viz_config.get('font_thickness', 2)
        self.update_interval = self.viz_config.get('update_interval', 0.1)

        # Controle de thread
        self.running = False
        self.thread = None
        self.current_frame = None
        self.window_name = "Pokemon Bot - Detecção em Tempo Real"

    def draw_bounding_boxes(self, base_image: np.ndarray) -> np.ndarray:
        """
        Desenha todas as bounding boxes na imagem.

        Args:
            base_image: Imagem base (formato OpenCV BGR)

        Returns:
            Imagem com as bounding boxes desenhadas
        """
        annotated = base_image.copy()

        # Itera por cada região definida no config
        for region_name, region_data in self.regions.items():
            coords = region_data['coords']  # [x1, y1, x2, y2]
            label = region_data['label']
            color = tuple(region_data['color'])  # BGR format

            # Desenha retângulo
            cv2.rectangle(
                annotated,
                (coords[0], coords[1]),  # Ponto superior esquerdo
                (coords[2], coords[3]),  # Ponto inferior direito
                color,
                self.thickness
            )

            # Prepara texto do label
            label_text = f"{label}"

            # Calcula tamanho do texto para criar fundo
            (text_width, text_height), baseline = cv2.getTextSize(
                label_text,
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                self.font_thickness
            )

            # Desenha fundo do label (para melhor legibilidade)
            label_y = coords[1] - 10
            if label_y < text_height + 10:
                label_y = coords[1] + text_height + 10  # Se não couber em cima, coloca embaixo

            cv2.rectangle(
                annotated,
                (coords[0], label_y - text_height - 5),
                (coords[0] + text_width + 5, label_y + 5),
                color,
                -1  # Preenchido
            )

            # Desenha o texto do label
            cv2.putText(
                annotated,
                label_text,
                (coords[0] + 2, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                (255, 255, 255),  # Branco
                self.font_thickness
            )

        return annotated

    def add_overlay_info(self, image: np.ndarray) -> np.ndarray:
        """
        Adiciona informações do bot como overlay na imagem.

        Args:
            image: Imagem para adicionar overlay

        Returns:
            Imagem com overlay de informações

        Informações exibidas:
        - Estado atual do bot
        - Estatísticas (batalhas, skins encontradas, etc)
        - FPS da visualização
        """
        overlay = image.copy()
        height, width = image.shape[:2]

        # Cria painel semi-transparente no topo
        panel_height = 100
        cv2.rectangle(
            overlay,
            (0, 0),
            (width, panel_height),
            (0, 0, 0),
            -1
        )

        # Aplica transparência
        alpha = 0.6
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

        # Adiciona texto de informações
        y_offset = 25
        line_height = 25

        # Estado atual
        if self.state_machine:
            state_text = f"Estado: {self.state_machine.get_state_name().upper()}"
            cv2.putText(
                image,
                state_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # TODO: Adicionar mais informações
        # - Último Pokémon detectado
        # - Número de batalhas
        # - Skins encontradas
        # - Tempo de execução

        return image

    def start(self) -> None:
        """
        Inicia a visualização em uma thread separada.

        A visualização roda em loop constante capturando a tela,
        desenhando as bounding boxes e exibindo em uma janela.
        """
        if not self.enabled:
            print("[VISUALIZAÇÃO] Visualização desabilitada no config")
            return

        if self.running:
            print("[VISUALIZAÇÃO] Já está rodando")
            return

        self.running = True
        self.thread = threading.Thread(target=self._visualization_loop, daemon=True)
        self.thread.start()
        print("[VISUALIZAÇÃO] Iniciada")

    def _visualization_loop(self) -> None:
        """
        Loop principal da visualização (roda em thread separada).

        TODO: Implementar loop de visualização
            1. Capturar tela
            2. Converter para OpenCV
            3. Desenhar bounding boxes
            4. Adicionar overlay de informações
            5. Mostrar na janela
            6. Aguardar update_interval
            7. Repetir
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        while self.running:
            try:
                # Captura a tela
                screenshot = self.screen.get_screenshot()
                frame = self.screen.pil_to_cv2(screenshot)

                # Desenha bounding boxes
                frame = self.draw_bounding_boxes(frame)

                # Adiciona overlay de informações
                frame = self.add_overlay_info(frame)

                # Armazena frame atual
                self.current_frame = frame

                # Exibe na janela
                cv2.imshow(self.window_name, frame)

                # Permite fechar com 'q' ou 'ESC'
                key = cv2.waitKey(int(self.update_interval * 1000))
                if key == ord('q') or key == 27:  # ESC
                    self.stop()
                    break

            except Exception as e:
                print(f"[VISUALIZAÇÃO] Erro: {e}")
                time.sleep(1)

        cv2.destroyAllWindows()

    def stop(self) -> None:
        """
        Para a visualização.
        """
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

        print("[VISUALIZAÇÃO] Parada")

    def save_current_frame(self, filename: str) -> bool:
        """
        Salva o frame atual em disco.

        Args:
            filename: Nome do arquivo (ex: 'debug/frame.png')

        Returns:
            True se salvou com sucesso
        """
        if self.current_frame is None:
            print("[VISUALIZAÇÃO] Nenhum frame disponível")
            return False

        cv2.imwrite(filename, self.current_frame)
        print(f"[VISUALIZAÇÃO] Frame salvo: {filename}")
        return True

    def highlight_region(self, region_name: str, duration: float = 2.0) -> None:
        """
        Destaca uma região específica temporariamente.

        Args:
            region_name: Nome da região para destacar
            duration: Tempo em segundos para manter o destaque

        TODO: Implementar sistema de highlight
            - Aumentar espessura da bounding box
            - Adicionar efeito piscante
            - Útil para debug visual
        """
        pass


class DebugVisualizer:
    """
    Ferramentas adicionais de visualização para debug.
    """

    @staticmethod
    def show_region_comparison(base_img: np.ndarray,
                               captured_img: np.ndarray,
                               title: str = "Comparação") -> None:
        """
        Mostra duas imagens lado a lado para comparação.

        Args:
            base_img: Imagem base (sprite padrão)
            captured_img: Imagem capturada (sprite da batalha)
            title: Título da janela

        Útil para debugar a detecção de skins.
        """
        # Redimensiona para mesmo tamanho se necessário
        h1, w1 = base_img.shape[:2]
        h2, w2 = captured_img.shape[:2]
        max_h = max(h1, h2)

        if h1 != max_h:
            base_img = cv2.resize(base_img, (int(w1 * max_h / h1), max_h))
        if h2 != max_h:
            captured_img = cv2.resize(captured_img, (int(w2 * max_h / h2), max_h))

        # Concatena lado a lado
        comparison = np.hstack([base_img, captured_img])

        # Adiciona labels
        cv2.putText(comparison, "BASE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(comparison, "CAPTURADO", (w1 + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(title, comparison)
        cv2.waitKey(0)
        cv2.destroyWindow(title)

    @staticmethod
    def show_ocr_preprocessing(original: np.ndarray,
                               processed: np.ndarray,
                               text_result: str) -> None:
        """
        Visualiza as etapas de pré-processamento do OCR.

        Args:
            original: Imagem original
            processed: Imagem após processamento
            text_result: Texto extraído pelo OCR
        """
        comparison = np.hstack([original, processed])

        # Adiciona o texto extraído
        cv2.putText(comparison, f"OCR: {text_result}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("OCR Preprocessing", comparison)
        cv2.waitKey(0)
        cv2.destroyWindow("OCR Preprocessing")


