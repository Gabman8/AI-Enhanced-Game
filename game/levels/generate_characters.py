from pathlib import Path

from characters.main_character import MainCharacter
from characters.regular_enemy import RegularEnemy
from scripts.generate_sprites import SPRITE_SHEETS, generate_sprites


NUMBER_OF_ENEMIES = 100
CHARACTERS = []
GAME_ROOT = Path(__file__).resolve().parent.parent
MAIN_CHARACTER_IMAGE_DIR = GAME_ROOT / "images" / "main_character"
SPRITE_SCALE = 1.0
SPRITE_SIZE = None


def _scale_surface(pygame, surface, size=SPRITE_SIZE):
    if size is None:
        return surface
    return pygame.transform.smoothscale(surface, size)


def _normalize_frame_size(pygame, surface, target_size):
    if surface.get_size() == target_size:
        return surface
    return pygame.transform.smoothscale(surface, target_size)


def _load_frames(pygame, folder):
    if not folder.exists():
        return []

    frames = []
    for image_path in sorted(folder.glob("frame_*.png")):
        frame = pygame.image.load(str(image_path)).convert_alpha()
        frames.append(_scale_surface(pygame, frame, size=SPRITE_SIZE))
    return frames


def _make_fallback_surface(pygame, size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


def _has_stale_frames(source_image, output_dir):
    if not source_image.exists() or not output_dir.exists():
        return True

    frame_files = sorted(output_dir.glob("frame_*.png"))
    if not frame_files:
        return True

    latest_frame_time = max(frame.stat().st_mtime for frame in frame_files)
    return source_image.stat().st_mtime > latest_frame_time


def _ensure_main_character_frames():
    for sprite_name, source_image in SPRITE_SHEETS.items():
        output_dir = MAIN_CHARACTER_IMAGE_DIR / sprite_name
        if _has_stale_frames(source_image, output_dir):
            generate_sprites()
            return


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
