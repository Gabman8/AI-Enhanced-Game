from characters.main_character import MainCharacter
CHARACTER_DATA = {}
def generate_characters(pygame):
    main_character = MainCharacter("John", ["strength", "speed"], "brave", "main_character", 100, 100);
    main_character_image = pygame.image.load(main_character.standing_image).convert_alpha()
    main_character_image = pygame.transform.scale(main_character_image, 
                                              (main_character_image.get_width() * 1.2, 
                                               main_character_image.get_height() * 1.2))
    CHARACTER_DATA = {
        "numer_characters": 100,
        "image": "image",
        "type" : "main_character"
    }
    return CHARACTER_DATA
def get_main_character():
    if CHARACTER_DATA and CHARACTER_DATA["type"]:
        type = CHARACTER_DATA["type"]
        return type if type == "main_character"
