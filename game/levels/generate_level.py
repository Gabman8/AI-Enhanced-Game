from levels.generate_map import generate_map
from levels.generate_characters import generate_characters,get_enemies

def generate_level(pygame):
    map_data = generate_map("TimesSquare_background.png", 360, "Low")
    characters_data = generate_characters(pygame)
    enemies = get_enemies()

    return {
        "map_data": map_data,
        "character_data": characters_data,
        "enemies" : enemies
    }




