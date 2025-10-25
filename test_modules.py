"""
Script de Testes - VALIDAÇÃO DOS MÓDULOS
=========================================
Use este script para testar cada módulo individualmente ANTES de rodar o bot completo.

Uso:
    python test_modules.py
"""

import json
import time
from pathlib import Path

# Imports dos módulos
from modules.screen import ScreenCapture
from modules.detection import BattleDetector, PokemonIdentifier, SpriteComparator
from modules.controls import GameController
from modules.visualizer import BoundingBoxVisualizer


def load_config():
    """Carrega config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def test_screen_capture():
    """Teste 1: Captura de Tela"""
    print("\n" + "=" * 60)
    print("TESTE 1: CAPTURA DE TELA")
    print("=" * 60)

    config = load_config()
    screen = ScreenCapture(config)

    # Valida regiões
    if not screen.validate_regions():
        print("\n⚠️  Ajuste as coordenadas no config.json antes de continuar!")
        return False

    # Testa captura de cada região
    print("\nCapturando todas as regiões...")
    regions = screen.get_all_regions()

    for name, img in regions.items():
        if img:
            filename = f"debug/test_region_{name}.png"
            screen.save_screenshot(img, filename)

    print("\n✅ Teste de captura concluído!")
    print("   Verifique as imagens em debug/test_region_*.png")
    return True


def test_visualization():
    """Teste 2: Visualização com Bounding Boxes"""
    print("\n" + "=" * 60)
    print("TESTE 2: VISUALIZAÇÃO")
    print("=" * 60)
    print("\nAbrindo janela de visualização por 10 segundos...")
    print("Verifique se as bounding boxes estão nas posições corretas!")

    config = load_config()
    screen = ScreenCapture(config)
    visualizer = BoundingBoxVisualizer(config, screen)

    # Inicia visualização
    visualizer.start()

    # Aguarda 10 segundos
    for i in range(10, 0, -1):
        print(f"Fechando em {i}s... (ou pressione 'q' na janela)", end='\r')
        time.sleep(1)
        if not visualizer.running:
            break

    visualizer.stop()
    print("\n✅ Teste de visualização concluído!")
    return True


def test_battle_detection():
    """Teste 3: Detecção de Batalha"""
    print("\n" + "=" * 60)
    print("TESTE 3: DETECÇÃO DE BATALHA")
    print("=" * 60)

    config = load_config()
    screen = ScreenCapture(config)
    detector = BattleDetector(config, screen)

    print("\nTestando detecção por 10 segundos...")
    print("Inicie uma batalha no jogo para testar!")

    for i in range(50):  # 10 segundos (0.2s cada)
        in_battle = detector.is_in_battle()
        status = "🔴 BATALHA" if in_battle else "🟢 Farm"
        print(f"{status}", end='\r')
        time.sleep(0.2)

    print("\n✅ Teste de detecção concluído!")
    return True


def test_ocr():
    """Teste 4: OCR do Nome"""
    print("\n" + "=" * 60)
    print("TESTE 4: OCR DO NOME DO POKÉMON")
    print("=" * 60)

    config = load_config()
    screen = ScreenCapture(config)
    identifier = PokemonIdentifier(config, screen)

    print("\nInicie uma batalha e aguarde 3 segundos...")
    time.sleep(3)

    print("Tentando extrair nome do Pokémon...")
    name = identifier.get_pokemon_name()

    if name:
        print(f"\n✅ Nome detectado: '{name.upper()}'")
    else:
        print("\n❌ Não conseguiu detectar o nome")
        print("   Verifique se:")
        print("   - Está em uma batalha")
        print("   - As coordenadas da região 'pokemon_name' estão corretas")
        print("   - O Tesseract está instalado corretamente")

    return name is not None


def test_sprite_comparison():
    """Teste 5: Comparação de Sprites"""
    print("\n" + "=" * 60)
    print("TESTE 5: COMPARAÇÃO DE SPRITES")
    print("=" * 60)

    config = load_config()
    screen = ScreenCapture(config)
    comparator = SpriteComparator(config, screen)

    # Verifica se há sprites base
    sprite_dir = Path("assets/base_sprites")
    sprites = list(sprite_dir.glob("*.png"))

    if not sprites:
        print("\n❌ Nenhum sprite base encontrado em assets/base_sprites/")
        print("   Adicione pelo menos um sprite base para testar!")
        return False

    print(f"\nSprites base encontrados: {len(sprites)}")
    for sprite in sprites:
        print(f"  - {sprite.stem}")

    # Testa com primeiro sprite
    test_pokemon = sprites[0].stem
    print(f"\nTestando comparação com '{test_pokemon}'...")
    print("Inicie uma batalha com este Pokémon em 3 segundos...")
    time.sleep(3)

    is_skin, difference = comparator.is_pokemon_skinned(test_pokemon)

    print(f"\nResultado:")
    print(f"  - Diferença: {difference:.2f}")
    print(f"  - Threshold: {comparator.hash_threshold}")
    print(f"  - É skin? {'SIM ✨' if is_skin else 'NÃO'}")

    # Salva comparação visual
    comparator.save_comparison_debug(test_pokemon, difference)

    print("\n✅ Teste de comparação concluído!")
    print("   Verifique debug/comparison_*.png para ver a comparação visual")
    return True


def test_controls():
    """Teste 6: Controles"""
    print("\n" + "=" * 60)
    print("TESTE 6: CONTROLES")
    print("=" * 60)

    config = load_config()
    controller = GameController(config)

    print("\nFoque na janela do jogo em 3 segundos...")
    time.sleep(3)

    print("\nTestando movimento...")
    controller.move_between_tiles()

    print("\nTestando fuga (se estiver em batalha)...")
    controller.flee_battle()

    print("\n✅ Teste de controles concluído!")
    print("   Verifique se os comandos foram executados corretamente")
    return True


def run_all_tests():
    """Executa todos os testes em sequência"""
    print("=" * 60)
    print("POKEMON BOT - SUITE DE TESTES")
    print("=" * 60)
    print("\nEsta suite vai testar todos os módulos implementados.")
    print("Siga as instruções de cada teste.\n")

    input("Pressione ENTER para começar...")

    # Cria diretórios necessários
    Path("debug").mkdir(exist_ok=True)
    Path("assets/base_sprites").mkdir(parents=True, exist_ok=True)

    tests = [
        ("Captura de Tela", test_screen_capture),
        ("Visualização", test_visualization),
        ("Detecção de Batalha", test_battle_detection),
        ("OCR", test_ocr),
        ("Comparação de Sprites", test_sprite_comparison),
        ("Controles", test_controls),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\nTestes interrompidos pelo usuário")
            break
        except Exception as e:
            print(f"\n❌ Erro no teste '{test_name}': {e}")
            results[test_name] = False

        # Pausa entre testes
        if test_name != tests[-1][0]:
            input("\nPressione ENTER para próximo teste...")

    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\nTotal: {passed_count}/{total_count} testes passaram")

    if passed_count == total_count:
        print("\n🎉 Todos os testes passaram! O bot está pronto para uso.")
    else:
        print("\n⚠️  Alguns testes falharam. Revise as configurações.")


def interactive_menu():
    """Menu interativo para escolher testes"""
    while True:
        print("\n" + "=" * 60)
        print("MENU DE TESTES")
        print("=" * 60)
        print("\n1. Testar Captura de Tela")
        print("2. Testar Visualização")
        print("3. Testar Detecção de Batalha")
        print("4. Testar OCR")
        print("5. Testar Comparação de Sprites")
        print("6. Testar Controles")
        print("7. Executar TODOS os testes")
        print("0. Sair")

        choice = input("\nEscolha uma opção: ")

        tests = {
            '1': test_screen_capture,
            '2': test_visualization,
            '3': test_battle_detection,
            '4': test_ocr,
            '5': test_sprite_comparison,
            '6': test_controls,
            '7': run_all_tests,
        }

        if choice == '0':
            print("\nEncerrando...")
            break
        elif choice in tests:
            try:
                tests[choice]()
            except KeyboardInterrupt:
                print("\n\nTeste interrompido")
            except Exception as e:
                print(f"\n❌ Erro: {e}")
        else:
            print("\n❌ Opção inválida!")


if __name__ == "__main__":
    """
    Ponto de entrada do script de testes.

    Uso:
        python test_modules.py           # Menu interativo
        python test_modules.py --all     # Executa todos os testes
    """
    import sys

    if '--all' in sys.argv:
        run_all_tests()
    else:
        interactive_menu()