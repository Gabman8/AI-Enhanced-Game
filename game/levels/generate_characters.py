from pathlib import Path

from characters.main_character import MainCharacter
from characters.regular_enemy import RegularEnemy
from scripts.generate_sprites import generate_sprites


NUMBER_OF_ENEMIES = 100
CHARACTERS = []
GAME_ROOT = Path(__file__).resolve().parent.parent
MAIN_CHARACTER_IMAGE_DIR = GAME_ROOT / "images" / "main_character"
SPRITE_SCALE = 1.2


def _scale_surface(pygame, surface, scale=SPRITE_SCALE):
    width = int(surface.get_width() * scale)
    height = int(surface.get_height() * scale)
    return pygame.transform.scale(surface, (width, height))


def _load_frames(pygame, folder):
    if not folder.exists():
        return []

    frames = []
    for image_path in sorted(folder.glob("frame_*.png")):
        frame = pygame.image.load(str(image_path)).convert_alpha()
        frames.append(_scale_surface(pygame, frame))
    return frames


def _make_fallback_surface(pygame, size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


def _ensure_main_character_frames():
    running_dir = MAIN_CHARACTER_IMAGE_DIR / "running"
    attack_dir = MAIN_CHARACTER_IMAGE_DIR / "attack"
    has_running = any(running_dir.glob("frame_*.png")) if running_dir.exists() else False
    has_attack = any(attack_dir.glob("frame_*.png")) if attack_dir.exists() else False

    if not has_running or not has_attack:
        generate_sprites()


def generate_characters(pygame, characters=None):
    _ensure_main_character_frames()

    main_character = MainCharacter()
    main_character.running_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "running")
    main_character.attacking_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "attack")

    if main_character.running_images:
        main_character.standing_image = main_character.running_images[0]
    else:
        main_character.standing_image = _make_fallback_surface(pygame, (90, 140), (40, 90, 180, 255))

    characters = [main_character]
    for _ in range(NUMBER_OF_ENEMIES):
        enemy = RegularEnemy("Goblin", ["attack"], "hostile", "regular_enemy", 50, 20)
        enemy.standing_image = _make_fallback_surface(pygame, (70, 120), (120, 30, 30, 255))
        characters.append(enemy)

    global CHARACTERS
    CHARACTERS = characters
    return CHARACTERS


def get_main_character():
    global CHARACTERS
    if CHARACTERS:
        for character in CHARACTERS:
            if character.type == "main_character":
                return character
    return None
