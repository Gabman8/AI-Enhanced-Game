from pathlib import Path
from characters.character import Character
from scripts.generate_sprites import SPRITE_SHEETS
import random


NUMBER_OF_ENEMIES = 2
CHARACTERS = []
GAME_ROOT = Path(__file__).resolve().parent.parent
MAIN_CHARACTER = "main_character"
REGULAR_ENEMY = "regular_enemy"
STRONG_ENEMY =  "strong_enemy"
FINAL_BOSS = "final_boss"
MAIN_CHARACTER_IMAGE_DIR = GAME_ROOT / "images" / MAIN_CHARACTER
REGULAR_ENEMY_IMAGE_DIR = GAME_ROOT / "images" / REGULAR_ENEMY
STRONG_ENEMY_IMAGE_DIR = GAME_ROOT / "images" / STRONG_ENEMY

SPRITE_SCALE = 1
SPRITE_SIZE = (260, 340)  # +30% from (200, 260) 

ENEMY_TYPE_STATS = {
    REGULAR_ENEMY: {
        "health": 60,
        "strength": 20,
        "speed": 260,
        "personality": "hostile",
    },
    STRONG_ENEMY: {
        "health": 100,
        "strength": 40,
        "speed": 220,
        "personality": "aggressive",
    },
    FINAL_BOSS: {
        "health": 170,
        "strength": 60,
        "speed": 200,
        "personality": "merciless",
    },
}


def _scale_surface(pygame, surface, size=SPRITE_SIZE):
    if size is None:
        return surface
    return pygame.transform.smoothscale(surface, size)


def _normalize_frame_size(pygame, surface, target_size):
    if surface.get_size() == target_size:
        return surface
    return pygame.transform.smoothscale(surface, target_size)


def _load_frames(pygame, folder, scale_size=SPRITE_SIZE):
    if not folder.exists():
        return []

    frames = []
    for image_path in sorted(folder.glob("frame_*.png")):
        frame = pygame.image.load(str(image_path)).convert_alpha()
        frames.append(_scale_surface(pygame, frame, size=scale_size))
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


def _create_enemy(pygame, enemy_type_data, health_scale=1.0, strength_scale=1.0, speed_scale=1.0):
    stats = enemy_type_data["stats"]
    running_images = _load_frames(pygame, enemy_type_data["image_dir"] / "running", SPRITE_SIZE)
    attacking_images = _load_frames(pygame, enemy_type_data["image_dir"] / "attack", SPRITE_SIZE)
    # Death sprites at 55% size to avoid distortion at death
    death_size = (int(SPRITE_SIZE[0] * 0.55), int(SPRITE_SIZE[1] * 0.55))
    death_images = _load_frames(pygame, enemy_type_data["image_dir"] / "death", death_size)

    standing_image = running_images[0] if running_images else _make_fallback_surface(pygame, (90, 140), (160, 40, 40, 255))
    enemy = Character(
        "Enemy",
        ["attack"],
        stats["personality"],
        enemy_type_data["type"],
        int(stats["health"] * health_scale),
        int(stats["strength"] * strength_scale),
        0.5,
        0.2,
        0.5,
        standing_image=standing_image,
        running_images=running_images,
        attacking_images=attacking_images,
        death_images=death_images,
    )
    enemy.speed = int(stats["speed"] * speed_scale)
    enemy.max_health = enemy.health
    return enemy


def generate_characters(
    pygame,
    enemy_count=NUMBER_OF_ENEMIES,
    strong_enemy_prob=0.35,
    health_scale=1.0,
    strength_scale=1.0,
    speed_scale=1.0,
):
    _ensure_main_character_frames()

    main_character = Character("GigaChad", ["attack", "talk"], "brave", "main_character", 100, 100, 1, 0, 1)
    main_character.running_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "running")
    main_character.attacking_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "attack")

    if main_character.running_images:
        main_character.standing_image = main_character.running_images[0]
    else:
        main_character.standing_image = _make_fallback_surface(pygame, (90, 140), (40, 90, 180, 255))

    characters = [main_character]
    for _ in range(int(enemy_count)):
        enemy_type_data = generate_enemy_type(strong_enemy_prob)
        enemy = _create_enemy(
            pygame,
            enemy_type_data,
            health_scale=health_scale,
            strength_scale=strength_scale,
            speed_scale=speed_scale,
        )
        characters.append(enemy)

    global CHARACTERS
    CHARACTERS = characters
    return CHARACTERS

def generate_enemy_type(strong_enemy_prob=0.35):
    number = random.randint(1, 100)
    if number <= int(strong_enemy_prob * 100):
        return {
            "type": STRONG_ENEMY,
            "image_dir": STRONG_ENEMY_IMAGE_DIR,
            "stats": ENEMY_TYPE_STATS[STRONG_ENEMY],
        }
    return {
        "type": REGULAR_ENEMY,
        "image_dir": REGULAR_ENEMY_IMAGE_DIR,
        "stats": ENEMY_TYPE_STATS[REGULAR_ENEMY],
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

