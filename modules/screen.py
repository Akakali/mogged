"""
Módulo de Captura de Tela
=========================
Responsável por todas as operações de screenshot e manipulação de regiões da tela.

Funcionalidades:
- Captura de regiões específicas da tela
- Conversão entre formatos de imagem (PIL <-> OpenCV)
- Desenho de bounding boxes para visualização
"""

from PIL import ImageGrab, Image
import numpy as np
import cv2
from typing import Tuple, List, Optional


class ScreenCapture:
    """
    Gerencia todas as operações de captura de tela do bot.
    """

    def __init__(self, config: dict):
        """
        Inicializa o módulo de captura de tela.

        Args:
            config: Dicionário com configurações do bot
        """
        self.config = config
        self.regions = config.get('regions', {})
        self.viz_config = config.get('visualization', {})

    def get_screenshot(self, region_coords: List[int] = None) -> Image.Image:
        """
        Captura um screenshot de uma região específica ou da tela inteira.

        Args:
            region_coords: Lista [x1, y1, x2, y2] definindo a região.
                          Se None, captura a tela inteira.

        Returns:
            Objeto PIL.Image com o screenshot

        Example:
            >>> screen = ScreenCapture(config)
            >>> img = screen.get_screenshot([100, 100, 200, 200])
        """
        if region_coords:
            bbox = tuple(region_coords)
            return ImageGrab.grab(bbox=bbox)
        return ImageGrab.grab()

    def get_region_by_name(self, region_name: str) -> Image.Image:
        """
        Captura uma região específica usando o nome definido no config.

        Args:
            region_name: Nome da região no config.json (ex: 'pokemon_name')

        Returns:
            Imagem da região capturada

        Raises:
            KeyError: Se a região não existir no config
        """
        if region_name not in self.regions:
            raise KeyError(f"Região '{region_name}' não encontrada no config")

        coords = self.regions[region_name]['coords']
        return self.get_screenshot(coords)

    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """
        Converte uma imagem PIL para formato OpenCV (numpy array).

        Args:
            pil_image: Imagem no formato PIL

        Returns:
            Imagem no formato OpenCV (BGR)
        """
        # Converte PIL RGB para numpy array
        img_array = np.array(pil_image)

        # Converte RGB para BGR (formato do OpenCV)
        if len(img_array.shape) == 3:
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        return img_array

    def cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """
        Converte uma imagem OpenCV para formato PIL.

        Args:
            cv2_image: Imagem no formato OpenCV (BGR)

        Returns:
            Imagem no formato PIL (RGB)
        """
        if len(cv2_image.shape) == 3:
            rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_image)
        return Image.fromarray(cv2_image)

    def draw_bounding_boxes(self, base_image: np.ndarray = None) -> np.ndarray:
        """
        Desenha todas as bounding boxes definidas no config sobre a imagem.

        Esta função é o CORE da visualização. Ela pega a tela atual e desenha
        retângulos coloridos com labels em cada região de detecção.

        Args:
            base_image: Imagem base (OpenCV format). Se None, captura a tela.

        Returns:
            Imagem com as bounding boxes desenhadas

        TODO: Implementar lógica de desenho
            1. Se base_image é None, capturar tela inteira
            2. Para cada região no config['regions']:
                - Extrair coords, label e color
                - Desenhar retângulo com cv2.rectangle()
                - Adicionar texto com cv2.putText()
            3. Retornar imagem anotada
        """
        # Se não foi fornecida imagem, captura a tela
        if base_image is None:
            screenshot = self.get_screenshot()
            base_image = self.pil_to_cv2(screenshot)

        # Cria uma cópia para não modificar a original
        annotated_image = base_image.copy()

        # TODO: Implementar desenho das bounding boxes
        # for region_name, region_data in self.regions.items():
        #     coords = region_data['coords']  # [x1, y1, x2, y2]
        #     label = region_data['label']
        #     color = tuple(region_data['color'])  # BGR format
        #
        #     # Desenha retângulo
        #     cv2.rectangle(annotated_image,
        #                   (coords[0], coords[1]),
        #                   (coords[2], coords[3]),
        #                   color,
        #                   self.viz_config['bbox_thickness'])
        #
        #     # Desenha label acima do retângulo
        #     cv2.putText(annotated_image,
        #                 label,
        #                 (coords[0], coords[1] - 10),
        #                 cv2.FONT_HERSHEY_SIMPLEX,
        #                 self.viz_config['font_scale'],
        #                 color,
        #                 self.viz_config['font_thickness'])

        return annotated_image

    def save_screenshot(self, image: Image.Image, filename: str) -> None:
        """
        Salva uma imagem em disco.

        Args:
            image: Imagem PIL ou OpenCV
            filename: Nome do arquivo (ex: 'debug/screenshot_001.png')
        """
        if isinstance(image, np.ndarray):
            image = self.cv2_to_pil(image)

        image.save(filename)
        print(f"Screenshot salvo: {filename}")


# Função auxiliar para uso rápido
def quick_capture(region_coords: List[int]) -> Image.Image:
    """
    Função de conveniência para captura rápida sem instanciar a classe.

    Args:
        region_coords: [x1, y1, x2, y2]

    Returns:
        Imagem PIL da região
    """
    return ImageGrab.grab(bbox=tuple(region_coords))
