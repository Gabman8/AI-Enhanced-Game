from levels.generate_map import generate_map
from levels.generate_characters import generate_characters, get_enemies
from levels.adjust_dificulty import DifficultyAdjuster


def generate_level(pygame, level=1, previous_stats=None):
    map_data = generate_map(360, "Low", level=level)

    adjuster = DifficultyAdjuster()
    config = adjuster.suggest_level_config(level, previous_stats)

    characters_data = generate_characters(
        pygame,
        enemy_count=config["enemy_count"],
        strong_enemy_prob=config["strong_enemy_prob"],
        health_scale=config["enemy_health_scale"],
        strength_scale=config["enemy_strength_scale"],
        speed_scale=config["enemy_speed_scale"],
    )
    enemies = get_enemies()

    return {
        "map_data": map_data,
        "character_data": characters_data,
        "enemies": enemies,
        "difficulty_config": config,
        "difficulty_adjuster": adjuster,
    }




