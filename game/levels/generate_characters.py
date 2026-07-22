from pathlib import Path
from characters.character import Character
from scripts.generate_sprites import SPRITE_SHEETS
import random


NUMBER_OF_ENEMIES = 3
CHARACTERS = []
GAME_ROOT = Path(__file__).resolve().parent.parent
MAIN_CHARACTER = "main_character"
REGULAR_ENEMY = "regular_enemy"
STRONG_ENEMY =  "strong_enemy"
FINAL_BOSS = "final_boss"
MAIN_CHARACTER_IMAGE_DIR = GAME_ROOT / "images" / MAIN_CHARACTER
REGULAR_ENEMY_IMAGE_DIR = GAME_ROOT / "images" / REGULAR_ENEMY
STRONG_ENEMY_IMAGE_DIR = GAME_ROOT / "images" / STRONG_ENEMY

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
            return


def generate_characters(pygame, characters=None):
    _ensure_main_character_frames()

    main_character = Character("GigaChad",["attack","talk"], "brave", "main_character", 100, 100,1,0,1)
    main_character.running_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "running")
    main_character.attacking_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "attack")

    if main_character.running_images:
        main_character.standing_image = main_character.running_images[0]
    else:
        main_character.standing_image = _make_fallback_surface(pygame, (90, 140), (40, 90, 180, 255))

    characters = [main_character]
    for _ in range(NUMBER_OF_ENEMIES):
        result = generate_enemy_type()
        type= result["type"]
        image_dir = result["image_dir"]
        enemy = Character("regular",["attack"], "hostile", type, 60, 20, 0.5, 0.2, 0.5)
        enemy.running_images = _load_frames(pygame, image_dir / "running")
        enemy.attacking_images = _load_frames(pygame, image_dir / "attack")
        enemy.death_images = _load_frames(pygame, image_dir / "death")
        characters.append(enemy)

    global CHARACTERS
    CHARACTERS = characters
    return CHARACTERS

def generate_enemy_type():
    #35 percent probability to have a strong enemy
    strong_enemy_prob = 100
    number = random.randint(1,100)
    if number <= strong_enemy_prob:
        return {
            "type": STRONG_ENEMY,
            "image_dir": STRONG_ENEMY_IMAGE_DIR
        }
    else:
        return {
            "type": REGULAR_ENEMY,
            "image_dir": REGULAR_ENEMY_IMAGE_DIR
        }
    
def get_main_character():
    global CHARACTERS
    if CHARACTERS:
        for character in CHARACTERS:
            if character.type == "main_character":
                return character
    return None
def get_enemies():
    global CHARACTERS
    enemies = []
    if CHARACTERS:
        for character in CHARACTERS:
            if character.type != "main_character":
                enemies.append(character)
    return enemies

