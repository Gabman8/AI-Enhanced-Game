from characters.main_character import MainCharacter
from characters.regular_enemy import RegularEnemy
NUMBER_OF_ENEMIES = 100
CHARACTERS = []
def generate_characters(pygame, characters=None):
    main_character = MainCharacter("John", ["strength", "speed"], "brave", "main_character", 100, 100);
    main_character_image = pygame.image.load(main_character.standing_image).convert_alpha()
    main_character_image = pygame.transform.scale(main_character_image, 
                                              (main_character_image.get_width() * 1.2, 
                                               main_character_image.get_height() * 1.2))
    characters = []
    characters.append({
        "name": main_character.name,
        "abilities": main_character.abilities,
        "personality": main_character.personality,
        "type": main_character.type,
        "health": main_character.health,
        "strength": main_character.strength,
        "image": main_character_image,
        "walking_image": main_character.walking_image,
        "attacking_image": main_character.attacking_image
    })
    for i in range(NUMBER_OF_ENEMIES):
        enemy = RegularEnemy("Goblin", ["attack"], "hostile", "regular_enemy", 50, 20)
        enemy_image = pygame.image.load(enemy.standing_image).convert_alpha()
        enemy_image = pygame.transform.scale(enemy_image, 
                                             (enemy_image.get_width() * 1.2, 
                                              enemy_image.get_height() * 1.2))
        characters.append({
            "name": enemy.name,
            "abilities": enemy.abilities,
            "personality": enemy.personality,
            "type": enemy.type,
            "health": enemy.health,
            "strength": enemy.strength,
            "image": enemy_image,
            "walking_image": enemy.walking_image,
            "attacking_image": enemy.attacking_image
        })
        i+=1
    global CHARACTERS
    CHARACTERS = characters
    return CHARACTERS
def get_main_character():
    global CHARACTERS
    if CHARACTERS:
        for character in CHARACTERS:
            if character["type"] == "main_character":
                return character
    return None
