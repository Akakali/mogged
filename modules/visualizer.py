"""
Módulo de Visualização - IMPLEMENTADO
======================================
Exibe bounding boxes em tempo real sobre a tela.
"""

import cv2
import numpy as np
from typing import Optional, Dict, Tuple
import threading
import time


class BoundingBoxVisualizer:
    """
    Visualização em tempo real com bounding boxes coloridas.
    FEATURE PRINCIPAL DO BOT!
    """

    def __init__(self, config: dict, screen_capture, state_machine=None):
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

        # FPS counter
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()

    def draw_bounding_boxes(self, base_image: np.ndarray) -> np.ndarray:
        """
        Desenha todas as bounding boxes na imagem.

        Cada região tem:
        - Retângulo colorido
        - Label com fundo
        - Cor específica (definida no config)
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

            # Calcula tamanho do texto
            (text_width, text_height), baseline = cv2.getTextSize(
                label_text,
                cv2.FONT_HERSHEY_SIMPLEX,
                self.font_scale,
                self.font_thickness
            )

            # Posição do label (acima do retângulo)
            label_y = coords[1] - 10
            if label_y < text_height + 10:
                # Se não couber em cima, coloca embaixo
                label_y = coords[1] + text_height + 10

            # Desenha fundo do label (para melhor legibilidade)
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
        Adiciona informações do bot como overlay.

        Exibe:
        - Estado atual
        - FPS
        - Estatísticas (se disponível)
        """
        overlay = image.copy()
        height, width = image.shape[:2]

        # Cria painel semi-transparente no topo
        panel_height = 120
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
            state_name = self.state_machine.get_state_name().upper()
            state_color = self._get_state_color(state_name)

            cv2.putText(
                image,
                f"Estado: {state_name}",
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                state_color,
                2
            )
            y_offset += line_height

        # FPS
        cv2.putText(
            image,
            f"FPS: {self.fps:.1f}",
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (100, 200, 255),
            2
        )
        y_offset += line_height

        # Estatísticas (se disponível)
        if self.state_machine and hasattr(self.state_machine, 'statistics'):
            stats = self.state_machine.statistics
            if hasattr(stats, 'encounters'):
                cv2.putText(
                    image,
                    f"Batalhas: {stats.encounters} | Skins: {stats.skins_found}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 100),
                    2
                )

        # Instruções
        cv2.putText(
            image,
            "Pressione 'q' ou ESC para fechar",
            (10, height - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1
        )

        return image

    def _get_state_color(self, state_name: str) -> Tuple[int, int, int]:
        """Retorna cor baseada no estado."""
        color_map = {
            'IDLE': (128, 128, 128),      # Cinza
            'FARMING': (0, 255, 0),       # Verde
            'IN_BATTLE': (0, 165, 255),   # Laranja
            'PAUSED': (0, 255, 255),      # Amarelo
            'STOPPED': (0, 0, 255)        # Vermelho
        }
        return color_map.get(state_name, (255, 255, 255))

    def start(self) -> None:
        """Inicia a visualização em thread separada."""
        if not self.enabled:
            print("[VISUALIZAÇÃO] Desabilitada no config")
            return

        if self.running:
            print("[VISUALIZAÇÃO] Já está rodando")
            return

        self.running = True
        self.thread = threading.Thread(target=self._visualization_loop, daemon=True)
        self.thread.start()
        print("[VISUALIZAÇÃO] Thread iniciada")

    def _visualization_loop(self) -> None:
        """
        Loop principal da visualização (roda em thread separada).

        Fluxo:
        1. Captura tela
        2. Desenha bounding boxes
        3. Adiciona overlay
        4. Exibe na janela
        5. Calcula FPS
        6. Aguarda intervalo
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

                # Calcula FPS
                self.frame_count += 1
                elapsed = time.time() - self.fps_start_time
                if elapsed >= 1.0:
                    self.fps = self.frame_count / elapsed
                    self.frame_count = 0
                    self.fps_start_time = time.time()

                # Exibe na janela
                cv2.imshow(self.window_name, frame)

                # Permite fechar com 'q' ou 'ESC'
                key = cv2.waitKey(int(self.update_interval * 1000))
                if key == ord('q') or key == 27:  # ESC
                    print("\n[VISUALIZAÇÃO] Fechando por input do usuário")
                    self.stop()
                    break

            except Exception as e:
                print(f"[ERRO] Visualização: {e}")
                time.sleep(1)

        cv2.destroyAllWindows()
        print("[VISUALIZAÇÃO] Janela fechada")

    def stop(self) -> None:
        """Para a visualização."""
        if not self.running:
            return

        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        print("[VISUALIZAÇÃO] Thread parada")

    def save_current_frame(self, filename: str) -> bool:
        """
        Salva o frame atual em disco.

        Args:
            filename: Caminho do arquivo (ex: 'debug/skin_001.png')

        Returns:
            True se salvou com sucesso
        """
        if self.current_frame is None:
            print("[VISUALIZAÇÃO] Nenhum frame disponível")
            return False

        try:
            cv2.imwrite(filename, self.current_frame)
            print(f"[VISUALIZAÇÃO] Frame salvo: {filename}")
            return True
        except Exception as e:
            print(f"[ERRO] Salvar frame: {e}")
            return False

    def highlight_region(self, region_name: str, duration: float = 2.0) -> None:
        """
        Destaca uma região temporariamente com efeito piscante.

        TODO: Implementar efeito de highlight para debug visual
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
        Útil para debugar detecção de skins.
        """
        # Redimensiona para mesmo tamanho
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
        h, w = base_img.shape[:2]
        cv2.putText(comparison, "BASE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(comparison, "CAPTURADO", (w + 10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(title, comparison)
        print(f"[DEBUG] Pressione qualquer tecla para fechar '{title}'")
        cv2.waitKey(0)
        cv2.destroyWindow(title)

    @staticmethod
    def show_ocr_preprocessing(original: np.ndarray,
                               processed: np.ndarray,
                               text_result: str) -> None:
        """
        Visualiza as etapas de pré-processamento do OCR.
        """
        # Redimensiona se necessário
        if original.shape != processed.shape:
            h, w = original.shape[:2]
            processed = cv2.resize(processed, (w, h))

        comparison = np.hstack([original, processed])

        # Adiciona o texto extraído
        cv2.putText(comparison, f"OCR: {text_result}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("OCR Preprocessing", comparison)
        print(f"[DEBUG] Pressione qualquer tecla para fechar")
        cv2.waitKey(0)
        cv2.destroyWindow("OCR Preprocessing")