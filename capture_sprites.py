"""
FERRAMENTA DE CAPTURA DE SPRITES
=================================
Script auxiliar para capturar sprites base facilmente.

Uso:
    python capture_sprites.py
"""

import json
import time
from pathlib import Path
from modules.screen import ScreenCapture


class SpriteCaptureTool:
    """Ferramenta interativa para capturar sprites base."""

    def __init__(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        self.screen = ScreenCapture(self.config)
        self.sprite_dir = Path("assets/base_sprites")
        self.sprite_dir.mkdir(parents=True, exist_ok=True)

    def capture_sprite(self, pokemon_name: str) -> bool:
        """
        Captura e salva o sprite de um Pokémon.

        Args:
            pokemon_name: Nome do Pokémon (ex: "pikachu")

        Returns:
            True se capturou com sucesso
        """
        try:
            print(f"\n[CAPTURA] Capturando sprite de '{pokemon_name}'...")

            # Aguarda 2 segundos para usuário posicionar
            for i in range(2, 0, -1):
                print(f"  Capturando em {i}...", end='\r')
                time.sleep(1)

            # Captura região do sprite
            sprite_img = self.screen.get_region_by_name('pokemon_sprite')

            # Salva
            filename = self.sprite_dir / f"{pokemon_name.lower()}.png"
            sprite_img.save(filename)

            print(f"\n✅ Sprite salvo: {filename}")

            # Mostra preview
            print(f"   Tamanho: {sprite_img.size[0]}x{sprite_img.size[1]}px")

            return True

        except Exception as e:
            print(f"\n❌ Erro ao capturar: {e}")
            return False

    def batch_capture(self):
        """Modo de captura em lote."""
        print("\n" + "=" * 60)
        print("CAPTURA EM LOTE DE SPRITES")
        print("=" * 60)
        print("\nInstruções:")
        print("1. Entre em batalha com o Pokémon PADRÃO (sem skin)")
        print("2. Digite o nome do Pokémon")
        print("3. Aguarde a captura automática (2s)")
        print("4. Repita para cada Pokémon")
        print("\nDica: Mantenha sempre a mesma posição de câmera!")
        print("\nDigite 'sair' para finalizar\n")

        captured = []

        while True:
            pokemon_name = input("\nNome do Pokémon (ou 'sair'): ").strip()

            if pokemon_name.lower() in ['sair', 'exit', 'quit', 'q']:
                break

            if not pokemon_name:
                print("❌ Nome inválido!")
                continue

            # Remove caracteres especiais
            pokemon_name = ''.join(c for c in pokemon_name if c.isalnum())

            if self.capture_sprite(pokemon_name):
                captured.append(pokemon_name)

        # Resumo
        print("\n" + "=" * 60)
        print("RESUMO DA CAPTURA")
        print("=" * 60)
        print(f"\nTotal capturado: {len(captured)} sprites")

        if captured:
            print("\nSprites salvos:")
            for name in captured:
                print(f"  ✓ {name}.png")

        print(f"\nDiretório: {self.sprite_dir.absolute()}")
        print("\n✅ Captura concluída!")

    def list_sprites(self):
        """Lista todos os sprites base existentes."""
        sprites = list(self.sprite_dir.glob("*.png"))

        print("\n" + "=" * 60)
        print("SPRITES BASE DISPONÍVEIS")
        print("=" * 60)

        if not sprites:
            print("\n❌ Nenhum sprite encontrado!")
            print(f"   Diretório: {self.sprite_dir.absolute()}")
            return

        print(f"\nTotal: {len(sprites)} sprites\n")

        for sprite in sorted(sprites):
            from PIL import Image
            img = Image.open(sprite)
            print(f"  ✓ {sprite.stem:20s} ({img.size[0]}x{img.size[1]}px)")

    def verify_sprite(self, pokemon_name: str):
        """Verifica se um sprite existe e mostra preview."""
        filename = self.sprite_dir / f"{pokemon_name.lower()}.png"

        if not filename.exists():
            print(f"\n❌ Sprite '{pokemon_name}' não encontrado!")
            return

        from PIL import Image
        import cv2
        import numpy as np

        # Carrega e mostra
        img = Image.open(filename)
        img_cv = np.array(img)

        if len(img_cv.shape) == 3:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

        # Redimensiona para visualização melhor
        scale = 3
        h, w = img_cv.shape[:2]
        display = cv2.resize(img_cv, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)

        # Adiciona info
        info_panel = np.zeros((60, w * scale, 3), dtype=np.uint8)
        cv2.putText(info_panel, f"{pokemon_name.upper()}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(info_panel, f"Tamanho: {w}x{h}px", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        display_with_info = np.vstack([info_panel, display])

        cv2.imshow(f"Sprite: {pokemon_name}", display_with_info)
        print(f"\n✓ Mostrando sprite de '{pokemon_name}'")
        print("  Pressione qualquer tecla para fechar")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def recapture_sprite(self, pokemon_name: str):
        """Recaptura um sprite existente."""
        filename = self.sprite_dir / f"{pokemon_name.lower()}.png"

        if filename.exists():
            print(f"\n⚠️  Sprite '{pokemon_name}' já existe!")
            confirm = input("   Deseja sobrescrever? (s/N): ")

            if confirm.lower() != 's':
                print("   Cancelado.")
                return

        self.capture_sprite(pokemon_name)


def interactive_menu():
    """Menu interativo principal."""
    tool = SpriteCaptureTool()

    while True:
        print("\n" + "=" * 60)
        print("FERRAMENTA DE CAPTURA DE SPRITES")
        print("=" * 60)
        print("\n1. Capturar sprite único")
        print("2. Captura em lote (múltiplos sprites)")
        print("3. Listar sprites existentes")
        print("4. Verificar/visualizar sprite")
        print("5. Recapturar sprite existente")
        print("0. Sair")

        choice = input("\nEscolha uma opção: ").strip()

        try:
            if choice == '0':
                print("\nEncerrando...")
                break

            elif choice == '1':
                name = input("\nNome do Pokémon: ").strip()
                if name:
                    tool.capture_sprite(name)

            elif choice == '2':
                tool.batch_capture()

            elif choice == '3':
                tool.list_sprites()

            elif choice == '4':
                name = input("\nNome do Pokémon: ").strip()
                if name:
                    tool.verify_sprite(name)

            elif choice == '5':
                name = input("\nNome do Pokémon: ").strip()
                if name:
                    tool.recapture_sprite(name)

            else:
                print("\n❌ Opção inválida!")

        except KeyboardInterrupt:
            print("\n\nOperação cancelada")
        except Exception as e:
            print(f"\n❌ Erro: {e}")


def quick_capture_mode():
    """Modo rápido: captura 1 sprite e sai."""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python capture_sprites.py <nome_pokemon>")
        print("Exemplo: python capture_sprites.py pikachu")
        return

    pokemon_name = sys.argv[1]
    tool = SpriteCaptureTool()

    print(f"\n🎯 CAPTURA RÁPIDA: {pokemon_name}")
    print("Entre em batalha com o Pokémon PADRÃO agora!")

    tool.capture_sprite(pokemon_name)


if __name__ == "__main__":
    """
    Ponto de entrada.

    Uso:
        python capture_sprites.py              # Menu interativo
        python capture_sprites.py pikachu      # Captura rápida
    """
    import sys

    if len(sys.argv) > 1:
        quick_capture_mode()
    else:
        interactive_menu()