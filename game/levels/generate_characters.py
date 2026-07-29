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
FINAL_BOSS_IMAGE_DIR = GAME_ROOT / "images" / FINAL_BOSS

SPRITE_SCALE = 1
SPRITE_SIZE = (260, 340)  # +30% from (200, 260) 

ENEMY_TYPE_STATS = {
    REGULAR_ENEMY: {
        "name": "Maton Callejero",
        "display_name": "Maton Callejero",
        "health": 72,
        "strength": 24,
        "speed": 245,
        "personality": "hostile",
        "dialogue_style": "maton de barrio, sucio y provocador",
        "attack_cooldown": 0.9,
        "decision_interval": 0.9,
    },
    STRONG_ENEMY: {
        "name": "Ejecutor",
        "display_name": "Ejecutor Brutal",
        "health": 130,
        "strength": 42,
        "speed": 215,
        "personality": "aggressive",
        "dialogue_style": "luchador pesado, brutal y seguro de su fuerza",
        "attack_cooldown": 1.0,
        "decision_interval": 0.75,
    },
    FINAL_BOSS: {
        "name": "General Draven",
        "display_name": "General Draven",
        "health": 240,
        "strength": 72,
        "speed": 230,
        "personality": "merciless",
        "dialogue_style": "jefe final dominante, teatral y despiadado",
        "attack_cooldown": 1.45,
        "decision_interval": 0.55,
        "never_flee": True,
        "persists_on_death": False,
        "intro_line": "Se acabo. Yo decido quien cae aqui.",
        "entrance_announcement": "EL GENERAL DRAVEN ENTRA EN ESCENA",
        "death_line": "No huyo... caigo de frente.",
    },
}

ENEMY_IDENTITIES = {
    REGULAR_ENEMY: [
        {
            "name": "Navaja",
            "display_name": "Navaja",
            "dialogue_style": "maton de barrio, rapido para insultar y provocar",
        },
        {
            "name": "Tuerca",
            "display_name": "Tuerca",
            "dialogue_style": "buscapleitos chulesco, burlon y sucio",
        },
        {
            "name": "Rata",
            "display_name": "Rata",
            "dialogue_style": "cobarde fanfarron que amenaza demasiado",
        },
    ],
    STRONG_ENEMY: [
        {
            "name": "Maza",
            "display_name": "Maza",
            "dialogue_style": "verdugo pesado, seco y brutal",
        },
        {
            "name": "Toro",
            "display_name": "Toro de Hierro",
            "dialogue_style": "bestia de choque, segura de su fuerza",
        },
        {
            "name": "Brutus",
            "display_name": "Brutus",
            "dialogue_style": "luchador dominante que habla como si ya hubiera ganado",
        },
    ],
    FINAL_BOSS: [
        {
            "name": "General Draven",
            "display_name": "General Draven",
            "dialogue_style": "jefe final dominante, teatral y despiadado",
            "intro_line": "Se acabo. Yo decido quien cae aqui.",
            "entrance_announcement": "EL GENERAL DRAVEN ENTRA EN ESCENA",
            "death_line": "No huyo... caigo de frente.",
        },
    ],
}


# Handle scale surface for the current workflow.
def _scale_surface(pygame, surface, size=SPRITE_SIZE):
    if size is None:
        return surface
    return pygame.transform.smoothscale(surface, size)


# Handle normalize frame size for the current workflow.
def _normalize_frame_size(pygame, surface, target_size):
    if surface.get_size() == target_size:
        return surface
    return pygame.transform.smoothscale(surface, target_size)


# Load frames from the expected source.
def _load_frames(pygame, folder, scale_size=SPRITE_SIZE):
    if not folder.exists():
        return []

    frames = []
    for image_path in sorted(folder.glob("frame_*.png")):
        frame = pygame.image.load(str(image_path)).convert_alpha()
        frames.append(_scale_surface(pygame, frame, size=scale_size))
    return frames


# Handle make fallback surface for the current workflow.
def _make_fallback_surface(pygame, size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface


# Return whether stale frames matches the current conditions.
def _has_stale_frames(source_image, output_dir):
    if not source_image.exists() or not output_dir.exists():
        return True

    frame_files = sorted(output_dir.glob("frame_*.png"))
    if not frame_files:
        return True

    latest_frame_time = max(frame.stat().st_mtime for frame in frame_files)
    return source_image.stat().st_mtime > latest_frame_time


# Handle ensure main character frames for the current workflow.
def _ensure_main_character_frames():
    for sprite_name, source_image in SPRITE_SHEETS.items():
        output_dir = MAIN_CHARACTER_IMAGE_DIR / sprite_name
        if _has_stale_frames(source_image, output_dir):
            return


# Build enemy identity for the current workflow.
def _build_enemy_identity(enemy_type):
    identity_pool = ENEMY_IDENTITIES.get(enemy_type, [])
    if not identity_pool:
        return {}
    return random.choice(identity_pool).copy()


# Create enemy for the current workflow.
def _create_enemy(pygame, enemy_type_data, health_scale=1.0, strength_scale=1.0, speed_scale=1.0):
    stats = dict(enemy_type_data["stats"])
    stats.update(_build_enemy_identity(enemy_type_data["type"]))
    running_images = _load_frames(pygame, enemy_type_data["image_dir"] / "running", SPRITE_SIZE)
    attacking_images = _load_frames(pygame, enemy_type_data["image_dir"] / "attack", SPRITE_SIZE)
    # Death sprites lie horizontally, so give them extra width and less height.
    death_size = (int(SPRITE_SIZE[0] * 0.9), int(SPRITE_SIZE[1] * 0.44))
    death_images = _load_frames(pygame, enemy_type_data["image_dir"] / "death", death_size)

    standing_image = running_images[0] if running_images else _make_fallback_surface(pygame, (90, 140), (160, 40, 40, 255))
    enemy = Character(
        stats.get("name", "Enemy"),
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
        display_name=stats.get("display_name"),
        dialogue_style=stats.get("dialogue_style"),
        attack_cooldown=stats.get("attack_cooldown", 0.3),
        decision_interval=stats.get("decision_interval", 0.8),
        never_flee=stats.get("never_flee", False),
        persists_on_death=stats.get("persists_on_death", False),
        intro_line=stats.get("intro_line"),
        entrance_announcement=stats.get("entrance_announcement"),
        death_line=stats.get("death_line"),
    )
    enemy.speed = int(stats["speed"] * speed_scale)
    enemy.regular_speed = enemy.speed
    enemy.max_health = enemy.health
    return enemy


# Generate characters for the current workflow.
def generate_characters(
    pygame,
    enemy_count=NUMBER_OF_ENEMIES,
    strong_enemy_prob=0.35,
    boss_spawn_chance=0.0,
    force_final_boss=False,
    level=1,
    health_scale=1.0,
    strength_scale=1.0,
    speed_scale=1.0,
):
    _ensure_main_character_frames()

    main_character = Character(
        "GigaChad",
        ["attack", "talk"],
        "brave",
        "main_character",
        135,
        175,
        1,
        0,
        1,
        display_name="GigaChad",
        dialogue_style="heroe desafiante, confiado y algo fanfarron",
    )
    main_character.running_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "running")
    main_character.attacking_images = _load_frames(pygame, MAIN_CHARACTER_IMAGE_DIR / "attack")

    if main_character.running_images:
        main_character.standing_image = main_character.running_images[0]
    else:
        main_character.standing_image = _make_fallback_surface(pygame, (90, 140), (40, 90, 180, 255))

    characters = [main_character]

    total_enemy_count = max(1, int(enemy_count))
    has_final_boss = should_include_final_boss(
        boss_spawn_chance=boss_spawn_chance,
        force_final_boss=force_final_boss,
        level=level,
    )

    if has_final_boss:
        boss_enemy = _create_enemy(
            pygame,
            {
                "type": FINAL_BOSS,
                "image_dir": FINAL_BOSS_IMAGE_DIR,
                "stats": ENEMY_TYPE_STATS[FINAL_BOSS],
            },
            health_scale=health_scale,
            strength_scale=strength_scale,
            speed_scale=speed_scale,
        )
        characters.append(boss_enemy)

    remaining_enemy_count = total_enemy_count - (1 if has_final_boss else 0)
    for _ in range(remaining_enemy_count):
        enemy_type_data = generate_enemy_type(strong_enemy_prob=strong_enemy_prob)
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

# Return whether include final boss matches the current conditions.
def should_include_final_boss(
    boss_spawn_chance=0.0,
    force_final_boss=False,
    level=1,
):
    if force_final_boss:
        return True
    return level >= 10 and random.random() <= boss_spawn_chance


# Generate enemy type for the current workflow.
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
    
# Return main character for the current flow.
def get_main_character():
    global CHARACTERS
    if CHARACTERS:
        for character in CHARACTERS:
            if character.type == "main_character":
                return character
    return None
# Return enemies for the current flow.
def get_enemies():
    global CHARACTERS
    enemies = []
    if CHARACTERS:
        for character in CHARACTERS:
            if character.type != "main_character":
                enemies.append(character)
    return enemies

