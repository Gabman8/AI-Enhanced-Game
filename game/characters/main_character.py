
from characters.character import Character

class MainCharacter(Character):
    def __init__(self, name, abilities, personality, type, health, strength, 
                 standing_image=None, walking_image=None, attacking_image=None):
        
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image, walking_image, 
                         attacking_image)
        self.name = name if name else "Main Character"
        self.abilities = ["attack", "talk"]
        self.personality = "brave"
        self.type = "main_character"
        self.health = 100
        self.strength = 100
        self.standing_image = standing_image if standing_image else "characters/images/main_character.png"
        self.walking_image = walking_image if walking_image else []
        self.attacking_image = attacking_image if attacking_image else []