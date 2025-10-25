"""
Módulo de Captura de Tela - IMPLEMENTADO
=========================================
Todas as operações de screenshot e manipulação de imagens.
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
        """
        try:
            if region_coords:
                bbox = tuple(region_coords)
                return ImageGrab.grab(bbox=bbox)
            return ImageGrab.grab()
        except Exception as e:
            print(f"[ERRO] Captura de tela: {e}")
            # Retorna imagem vazia em caso de erro
            return Image.new('RGB', (640, 480), color='black')

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
            available = ', '.join(self.regions.keys())
            raise KeyError(
                f"Região '{region_name}' não encontrada no config. "
                f"Disponíveis: {available}"
            )

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
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            return cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        elif len(img_array.shape) == 3 and img_array.shape[2] == 4:
            # Se tiver canal alpha (RGBA)
            return cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)

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

    def save_screenshot(self, image: Image.Image, filename: str) -> None:
        """
        Salva uma imagem em disco.

        Args:
            image: Imagem PIL ou OpenCV
            filename: Nome do arquivo (ex: 'debug/screenshot_001.png')
        """
        try:
            if isinstance(image, np.ndarray):
                image = self.cv2_to_pil(image)

            image.save(filename)
            print(f"[SCREENSHOT] Salvo: {filename}")
        except Exception as e:
            print(f"[ERRO] Salvar screenshot: {e}")

    def get_all_regions(self) -> dict:
        """
        Captura todas as regiões definidas no config de uma vez.

        Returns:
            Dicionário com {nome_regiao: imagem_pil}
        """
        regions_captured = {}

        for region_name in self.regions.keys():
            try:
                regions_captured[region_name] = self.get_region_by_name(region_name)
            except Exception as e:
                print(f"[AVISO] Erro ao capturar região '{region_name}': {e}")
                regions_captured[region_name] = None

        return regions_captured

    def validate_regions(self) -> bool:
        """
        Valida se todas as regiões do config são válidas.

        Útil para testar configuração antes de iniciar o bot.

        Returns:
            True se todas as regiões são válidas
        """
        print("\n[VALIDAÇÃO] Testando regiões do config...")
        all_valid = True

        for region_name, region_data in self.regions.items():
            coords = region_data.get('coords', [])

            # Valida formato
            if len(coords) != 4:
                print(f"  ❌ '{region_name}': coords inválido (precisa de 4 valores)")
                all_valid = False
                continue

            # Valida valores
            x1, y1, x2, y2 = coords
            if x1 >= x2 or y1 >= y2:
                print(f"  ❌ '{region_name}': coordenadas inválidas (x1 < x2 e y1 < y2)")
                all_valid = False
                continue

            # Tenta capturar
            try:
                img = self.get_screenshot(coords)
                w, h = img.size
                print(f"  ✓ '{region_name}': {w}x{h}px OK")
            except Exception as e:
                print(f"  ❌ '{region_name}': erro ao capturar - {e}")
                all_valid = False

        if all_valid:
            print("\n✅ Todas as regiões estão configuradas corretamente!")
        else:
            print("\n⚠️  Algumas regiões têm problemas. Ajuste o config.json")

        return all_valid


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


# Ferramenta de calibração interativa
def calibrate_regions():
    """
    Ferramenta interativa para ajustar coordenadas das regiões.

    Uso:
        python -c "from modules.screen import calibrate_regions; calibrate_regions()"
    """
    print("=" * 60)
    print("CALIBRAÇÃO DE REGIÕES")
    print("=" * 60)
    print("\nEsta ferramenta ajuda a definir as coordenadas das regiões.")
    print("Use um programa como Paint ou ShareX para encontrar as coordenadas.")
    print("\nFormato: x1 y1 x2 y2")
    print("Onde (x1,y1) é o canto superior esquerdo")
    print("  e (x2,y2) é o canto inferior direito")
    print("\nPressione Ctrl+C para sair\n")

    regions = {}

    region_names = [
        'battle_indicator',
        'pokemon_name',
        'pokemon_sprite',
        'battle_ui'
    ]

    for region_name in region_names:
        print(f"\n--- {region_name} ---")
        try:
            coords_str = input(f"Digite as coordenadas (x1 y1 x2 y2): ")
            coords = [int(x) for x in coords_str.split()]

            if len(coords) != 4:
                print("❌ Erro: precisa de 4 valores")
                continue

            # Testa captura
            img = quick_capture(coords)
            print(f"✓ Região capturada: {img.size[0]}x{img.size[1]}px")

            # Pergunta cor
            print("Escolha uma cor para a bounding box:")
            print("  1 - Vermelho   2 - Verde   3 - Azul   4 - Amarelo")
            color_choice = input("Cor (1-4): ")

            colors = {
                '1': [255, 0, 0],    # Vermelho
                '2': [0, 255, 0],    # Verde
                '3': [0, 0, 255],    # Azul
                '4': [255, 255, 0]   # Amarelo
            }
            color = colors.get(color_choice, [255, 255, 255])

            regions[region_name] = {
                "coords": coords,
                "label": region_name.replace('_', ' ').title(),
                "color": color
            }

            print(f"✓ {region_name} configurado!")

        except KeyboardInterrupt:
            print("\n\nCalibração cancelada")
            return
        except Exception as e:
            print(f"❌ Erro: {e}")

    # Exibe JSON final
    print("\n" + "=" * 60)
    print("CONFIGURAÇÃO GERADA")
    print("=" * 60)
    print("\nCopie e cole isto no seu config.json:\n")

    import json
    print(json.dumps({"regions": regions}, indent=2))
    print("\n" + "=" * 60)