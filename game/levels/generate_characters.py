from characters.main_character import MainCharacter
from characters.regular_enemy import RegularEnemy

NUMBER_OF_ENEMIES = 100
CHARACTERS = []


def generate_characters(pygame, characters=None):
    generate_sprites()
    main_character = MainCharacter()
    main_character_image = pygame.image.load(main_character.standing_image).convert_alpha()
    main_character_image = pygame.transform.scale(
        main_character_image,
        (main_character_image.get_width() * 1.2, main_character_image.get_height() * 1.2),
    )
    main_character.standing_image = main_character_image

    characters = [main_character]
    for _ in range(NUMBER_OF_ENEMIES):
        enemy = RegularEnemy("Goblin", ["attack"], "hostile", "regular_enemy", 50, 20)
        enemy_image = pygame.image.load(enemy.standing_image).convert_alpha()
        enemy_image = pygame.transform.scale(
            enemy_image,
            (enemy_image.get_width() * 1.2, enemy_image.get_height() * 1.2),
        )
        enemy.standing_image = enemy_image
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

