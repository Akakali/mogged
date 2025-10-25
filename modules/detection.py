"""
Módulo de Detecção - IMPLEMENTADO
==================================
Detecção de batalha, OCR e comparação de sprites.
"""

import cv2
import numpy as np
import pytesseract
import imagehash
from PIL import Image
from typing import Tuple, Optional
import re
import os


class BattleDetector:
    """Detecta se o bot está em batalha."""

    def __init__(self, config: dict, screen_capture):
        self.config = config
        self.screen = screen_capture
        self.detection_config = config.get('detection', {})

        # Cache do estado anterior para detectar mudanças
        self.previous_frame = None
        self.battle_detected_frames = 0
        self.required_consecutive_frames = 3  # Precisa detectar 3 frames seguidos

    def is_in_battle(self) -> bool:
        """
        Detecta batalha através de análise de pixels na região indicadora.

        Método: Conta pixels brancos/claros que aparecem na UI de batalha.
        """
        try:
            # Captura a região indicadora
            indicator_img = self.screen.get_region_by_name('battle_indicator')
            img_cv = self.screen.pil_to_cv2(indicator_img)

            # Converte para escala de cinza
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # Conta pixels brancos/claros (threshold ajustável)
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            white_pixels = cv2.countNonZero(binary)
            total_pixels = binary.shape[0] * binary.shape[1]
            white_percentage = (white_pixels / total_pixels) * 100

            # Se mais de 20% dos pixels são brancos, provavelmente está em batalha
            is_battle = white_percentage > 20

            # Sistema de confirmação (evita falsos positivos)
            if is_battle:
                self.battle_detected_frames += 1
            else:
                self.battle_detected_frames = 0

            # Só confirma batalha após N frames consecutivos
            confirmed = self.battle_detected_frames >= self.required_consecutive_frames

            if confirmed and self.battle_detected_frames == self.required_consecutive_frames:
                print(f"[BATALHA] Detectada! ({white_percentage:.1f}% pixels claros)")

            return confirmed

        except Exception as e:
            print(f"[ERRO] Detecção de batalha: {e}")
            return False


class PokemonIdentifier:
    """Identifica o Pokémon através de OCR."""

    def __init__(self, config: dict, screen_capture):
        self.config = config
        self.screen = screen_capture
        self.ocr_lang = config.get('detection', {}).get('ocr_language', 'eng')

        # Configuração otimizada do Tesseract
        # PSM 7 = linha única de texto
        # OEM 3 = modo padrão (melhor para maioria dos casos)
        self.tesseract_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def get_pokemon_name(self) -> Optional[str]:
        """
        Extrai o nome do Pokémon usando OCR com pré-processamento robusto.
        """
        try:
            # Captura a região do nome
            name_img = self.screen.get_region_by_name('pokemon_name')
            img_cv = self.screen.pil_to_cv2(name_img)

            # === PRÉ-PROCESSAMENTO ===
            # 1. Converte para escala de cinza
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # 2. Aumenta o contraste
            gray = cv2.equalizeHist(gray)

            # 3. Aplica threshold adaptativo (melhor que threshold fixo)
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # 4. Remove ruído com morphological operations
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

            # 5. Resize para melhorar OCR (2x maior)
            h, w = cleaned.shape
            resized = cv2.resize(cleaned, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

            # Salva imagem processada para debug (opcional)
            if self.config.get('debug', False):
                cv2.imwrite('debug/ocr_preprocessed.png', resized)

            # === OCR ===
            text = pytesseract.image_to_string(
                resized,
                lang=self.ocr_lang,
                config=self.tesseract_config
            )

            # Limpa o resultado
            cleaned_name = self._clean_pokemon_name(text)

            if cleaned_name:
                print(f"[OCR] Nome detectado: '{cleaned_name}' (raw: '{text.strip()}')")
                return cleaned_name
            else:
                print(f"[OCR] Falhou ao extrair nome válido (raw: '{text.strip()}')")
                return None

        except Exception as e:
            print(f"[ERRO] OCR: {e}")
            return None

    def _clean_pokemon_name(self, raw_text: str) -> Optional[str]:
        """
        Limpa o texto do OCR para extrair apenas o nome do Pokémon.

        Remove: números, "LV", "LV.", quebras de linha, espaços, etc.
        """
        if not raw_text:
            return None

        # Remove tudo que não é letra (mantém apenas A-Z)
        clean = re.sub(r'[^A-Za-z]', '', raw_text)
        clean = clean.lower().strip()

        # Valida se tem pelo menos 3 caracteres (nome válido)
        if len(clean) >= 3:
            return clean

        return None


class SpriteComparator:
    """Compara sprites para detectar skins/variações."""

    def __init__(self, config: dict, screen_capture):
        self.config = config
        self.screen = screen_capture
        self.hash_threshold = config.get('detection', {}).get('hash_threshold', 5)
        self.sprite_dir = "assets/base_sprites/"

        # Cache de hashes para performance
        self._hash_cache = {}

    def is_pokemon_skinned(self, pokemon_name: str) -> Tuple[bool, float]:
        """
        Verifica se o Pokémon é diferente do padrão usando perceptual hashing.

        Retorna:
            (is_skin, difference_score)
        """
        try:
            # Valida se sprite base existe
            base_path = f"{self.sprite_dir}{pokemon_name}.png"
            if not os.path.exists(base_path):
                print(f"[AVISO] Sprite base não encontrado: {base_path}")
                return (False, -1.0)

            # Carrega sprite base
            base_sprite = Image.open(base_path)

            # Captura sprite atual da batalha
            captured_sprite = self.screen.get_region_by_name('pokemon_sprite')

            # === MÉTODO 1: PERCEPTUAL HASH (pHash) ===
            # Calcula hashes perceptuais
            base_hash = self._get_or_compute_hash(base_path, base_sprite)
            captured_hash = imagehash.phash(captured_sprite)

            # Calcula diferença (0 = idênticos, >0 = diferentes)
            difference = base_hash - captured_hash

            # Determina se é skin baseado no threshold
            is_skin = difference > self.hash_threshold

            print(f"[COMPARAÇÃO] Hash diff: {difference} (threshold: {self.hash_threshold})")

            # === MÉTODO 2: CONFIRMAÇÃO COM SSIM (opcional, mais preciso) ===
            if is_skin and self.config.get('use_ssim_confirmation', False):
                is_skin, ssim_score = self._confirm_with_ssim(base_sprite, captured_sprite)
                print(f"[SSIM] Confirmação: {ssim_score:.4f}")
                return (is_skin, float(difference))

            return (is_skin, float(difference))

        except FileNotFoundError:
            return (False, -1.0)
        except Exception as e:
            print(f"[ERRO] Comparação de sprites: {e}")
            return (False, -1.0)

    def _get_or_compute_hash(self, path: str, image: Image.Image):
        """Cache de hashes para melhor performance."""
        if path in self._hash_cache:
            return self._hash_cache[path]

        hash_value = imagehash.phash(image)
        self._hash_cache[path] = hash_value
        return hash_value

    def _confirm_with_ssim(self, base: Image.Image, captured: Image.Image) -> Tuple[bool, float]:
        """
        Confirmação adicional usando SSIM (Structural Similarity).
        Mais preciso mas também mais lento.
        """
        try:
            from skimage.metrics import structural_similarity as ssim

            # Converte para OpenCV e grayscale
            base_cv = self.screen.pil_to_cv2(base)
            captured_cv = self.screen.pil_to_cv2(captured)

            # Redimensiona para mesmo tamanho se necessário
            if base_cv.shape != captured_cv.shape:
                h, w = base_cv.shape[:2]
                captured_cv = cv2.resize(captured_cv, (w, h))

            # Converte para grayscale
            base_gray = cv2.cvtColor(base_cv, cv2.COLOR_BGR2GRAY)
            captured_gray = cv2.cvtColor(captured_cv, cv2.COLOR_BGR2GRAY)

            # Calcula SSIM (1.0 = idêntico, <0.95 = diferente)
            score = ssim(base_gray, captured_gray)

            # Se SSIM < threshold, confirma que é skin
            is_different = score < 0.95

            return (is_different, score)

        except ImportError:
            print("[AVISO] scikit-image não instalado, pulando confirmação SSIM")
            return (True, 0.0)  # Mantém resultado do phash
        except Exception as e:
            print(f"[ERRO] SSIM: {e}")
            return (True, 0.0)

    def save_comparison_debug(self, pokemon_name: str, difference: float) -> None:
        """Salva comparação visual para debug."""
        try:
            base_path = f"{self.sprite_dir}{pokemon_name}.png"
            base_sprite = Image.open(base_path)
            captured_sprite = self.screen.get_region_by_name('pokemon_sprite')

            # Converte para OpenCV
            base_cv = self.screen.pil_to_cv2(base_sprite)
            captured_cv = self.screen.pil_to_cv2(captured_sprite)

            # Redimensiona se necessário
            h, w = base_cv.shape[:2]
            if captured_cv.shape[:2] != (h, w):
                captured_cv = cv2.resize(captured_cv, (w, h))

            # Concatena lado a lado
            comparison = np.hstack([base_cv, captured_cv])

            # Adiciona labels
            cv2.putText(comparison, "BASE", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(comparison, f"CAPTURED (diff: {difference:.1f})",
                       (w + 10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Salva
            filename = f"debug/comparison_{pokemon_name}_{int(difference)}.png"
            cv2.imwrite(filename, comparison)
            print(f"[DEBUG] Comparação salva: {filename}")

        except Exception as e:
            print(f"[ERRO] Salvar debug: {e}")