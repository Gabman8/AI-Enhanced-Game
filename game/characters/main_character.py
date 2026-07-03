
from characters.character import Character

class MainCharacter(Character):
    def __init__(self, name, abilities, personality, type, health, strength, 
                 standing_image=None, walking_images=None, attacking_images=None):
        
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image, walking_images, 
                         attacking_images)
        self.name = name if name else "Main Character"
        self.abilities = ["attack", "talk"]
        self.personality = "brave"
        self.type = "main_character"
        self.health = 100
        self.strength = 100
        self.standing_image = standing_image if standing_image else "characters/images/main_character.png"
        self.walking_images = walking_images if walking_images else []
        self.attacking_images = attacking_images if attacking_images else []