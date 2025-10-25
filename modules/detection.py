"""
Módulo de Detecção
==================
Responsável por toda lógica de detecção, OCR e comparação de imagens.

Funcionalidades:
- Detecção de início/fim de batalha
- OCR para extrair nome do Pokémon
- Comparação de sprites usando perceptual hashing
- Análise de similaridade estrutural (SSIM)
"""

import cv2
import numpy as np
import pytesseract
import imagehash
from PIL import Image
from typing import Tuple, Optional
import re


class BattleDetector:
    """
    Detecta se o bot está em batalha ou farmando.
    """

    def __init__(self, config: dict, screen_capture):
        """
        Args:
            config: Configurações do bot
            screen_capture: Instância de ScreenCapture
        """
        self.config = config
        self.screen = screen_capture
        self.detection_config = config.get('detection', {})

    def is_in_battle(self) -> bool:
        """
        Verifica se o bot está em batalha através da região indicadora.

        Returns:
            True se estiver em batalha, False caso contrário

        TODO: Implementar detecção de batalha
            Método 1: Template Matching
                - Ter uma imagem template da UI de batalha
                - Usar cv2.matchTemplate() na região
                - Se match > threshold, retorna True

            Método 2: Detecção de Cor/Padrão
                - Verificar se há pixels específicos na região
                - Exemplo: contar pixels brancos ou de uma cor específica
                - Se count > threshold, retorna True

            Método 3: Comparação com estado anterior
                - Salvar frame anterior
                - Calcular diferença entre frames
                - Grande diferença = transição para batalha
        """
        try:
            # Captura a região indicadora
            indicator_img = self.screen.get_region_by_name('battle_indicator')

            # TODO: Implementar lógica de detecção
            # img_cv = self.screen.pil_to_cv2(indicator_img)
            # gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # white_pixels = cv2.countNonZero(gray > 200)
            # return white_pixels > THRESHOLD

            return False  # Placeholder

        except Exception as e:
            print(f"Erro na detecção de batalha: {e}")
            return False


class PokemonIdentifier:
    """
    Identifica o Pokémon através de OCR no nome.
    """

    def __init__(self, config: dict, screen_capture):
        """
        Args:
            config: Configurações do bot
            screen_capture: Instância de ScreenCapture
        """
        self.config = config
        self.screen = screen_capture
        self.ocr_lang = config.get('detection', {}).get('ocr_language', 'eng')

        # Configuração do Tesseract
        self.tesseract_config = '--psm 7 --oem 3'  # PSM 7: single line

    def get_pokemon_name(self) -> Optional[str]:
        """
        Extrai o nome do Pokémon usando OCR.

        Returns:
            Nome do Pokémon em minúsculas, ou None se falhar

        TODO: Implementar OCR robusto
            1. Capturar região do nome
            2. Pré-processar imagem:
                - Converter para escala de cinza
                - Aplicar threshold/binarização
                - Opcional: resize para melhor OCR
                - Opcional: aplicar blur para remover ruído
            3. Executar pytesseract.image_to_string()
            4. Limpar resultado:
                - Remover caracteres especiais
                - Extrair só o nome (remover "LV. X", etc)
                - Converter para lowercase
            5. Validar se o nome existe no banco de sprites
        """
        try:
            # Captura a região do nome
            name_img = self.screen.get_region_by_name('pokemon_name')
            img_cv = self.screen.pil_to_cv2(name_img)

            # TODO: Pré-processamento
            # gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            # preprocessed = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

            # TODO: OCR
            # text = pytesseract.image_to_string(preprocessed, lang=self.ocr_lang, config=self.tesseract_config)
            # cleaned_name = self._clean_pokemon_name(text)
            # return cleaned_name

            return "mankey"  # Placeholder para testes

        except Exception as e:
            print(f"Erro no OCR: {e}")
            return None

    def _clean_pokemon_name(self, raw_text: str) -> str:
        """
        Limpa o texto extraído do OCR.

        Args:
            raw_text: Texto bruto do OCR (ex: "MANKEY\nLV. 5")

        Returns:
            Nome limpo em lowercase (ex: "mankey")

        TODO: Implementar regex robusto
            - Remover números, "LV", "LV.", etc
            - Remover quebras de linha
            - Remover caracteres especiais
            - Manter apenas letras
        """
        # Remove tudo que não é letra
        clean = re.sub(r'[^a-zA-Z]', '', raw_text)
        return clean.lower().strip()


class SpriteComparator:
    """
    Compara sprites para detectar skins/variações.
    """

    def __init__(self, config: dict, screen_capture):
        """
        Args:
            config: Configurações do bot
            screen_capture: Instância de ScreenCapture
        """
        self.config = config
        self.screen = screen_capture
        self.hash_threshold = config.get('detection', {}).get('hash_threshold', 5)
        self.sprite_dir = "assets/base_sprites/"

    def is_pokemon_skinned(self, pokemon_name: str) -> Tuple[bool, float]:
        """
        Verifica se o Pokémon capturado é diferente do padrão (skin).

        Args:
            pokemon_name: Nome do Pokémon (ex: "mankey")

        Returns:
            Tupla (is_skin, difference_score)
            - is_skin: True se for skin, False se for padrão
            - difference_score: Valor numérico da diferença

        TODO: Implementar comparação robusta
            Método 1: Perceptual Hash (RECOMENDADO)
                1. Carregar sprite base: f"{sprite_dir}/{pokemon_name}.png"
                2. Capturar sprite da batalha
                3. Calcular hash de ambos: imagehash.phash()
                4. Calcular diferença: base_hash - captured_hash
                5. Se diferença > threshold: é skin

            Método 2: SSIM (Structural Similarity)
                1. Usar cv2 para calcular SSIM
                2. Score < 0.95: é skin

            Método 3: Híbrido (mais robusto)
                - Usar phash como filtro rápido
                - Se phash detectar diferença, confirmar com SSIM
        """
        try:
            # Carrega sprite base
            base_path = f"{self.sprite_dir}{pokemon_name}.png"
            base_sprite = Image.open(base_path)

            # Captura sprite atual da batalha
            captured_sprite = self.screen.get_region_by_name('pokemon_sprite')

            # TODO: Implementar comparação
            # Método 1: Perceptual Hash
            # base_hash = imagehash.phash(base_sprite)
            # captured_hash = imagehash.phash(captured_sprite)
            # difference = base_hash - captured_hash
            # is_skin = difference > self.hash_threshold
            # return (is_skin, float(difference))

            # Método 2: SSIM
            # base_cv = self.screen.pil_to_cv2(base_sprite)
            # captured_cv = self.screen.pil_to_cv2(captured_sprite)
            # similarity = self._calculate_ssim(base_cv, captured_cv)
            # is_skin = similarity < 0.95
            # return (is_skin, 1.0 - similarity)

            return (False, 0.0)  # Placeholder

        except FileNotFoundError:
            print(f"AVISO: Sprite base '{pokemon_name}.png' não encontrado!")
            return (False, -1.0)
        except Exception as e:
            print(f"Erro na comparação de sprites: {e}")
            return (False, -1.0)

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calcula Structural Similarity Index entre duas imagens.

        Args:
            img1, img2: Imagens no formato OpenCV

        Returns:
            Score de similaridade (0.0 a 1.0)

        TODO: Implementar SSIM usando cv2 ou skimage
        """
        # from skimage.metrics import structural_similarity as ssim
        # gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        # gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        # score = ssim(gray1, gray2)
        # return score

        return 1.0  # Placeholder

    def save_comparison_debug(self, pokemon_name: str,
                              base_sprite: Image.Image,
                              captured_sprite: Image.Image,
                              difference: float) -> None:
        """
        Salva imagens lado-a-lado para debug visual.

        Args:
            pokemon_name: Nome do Pokémon
            base_sprite: Sprite base
            captured_sprite: Sprite capturado
            difference: Score de diferença

        TODO: Criar imagem comparativa
            - Colocar sprites lado a lado
            - Adicionar texto com o score
            - Salvar em debug/comparisons/
        """
        pass
