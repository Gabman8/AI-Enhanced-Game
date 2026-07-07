
from characters.character import Character

class RegularEnemy(Character):
    def __init__(self, name, abilities, personality, type, health, strength, 
                 standing_image=None, walking_image=None, attacking_image=None):
        
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image, walking_image, 
                         attacking_image)
        self.name = "Regular Enemy"
        self.abilities = ["attack"]
        self.personality = "hostile"
        self.type = "regular_enemy"
        self.health = 50
        self.strength = 20
        self.standing_image = standing_image if standing_image else "characters/images/viking.png"
        self.walking_image = walking_image if walking_image else []
        self.attacking_image = attacking_image if attacking_image else []
