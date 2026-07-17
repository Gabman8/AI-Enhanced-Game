
from characters.character import Character

class RegularEnemy(Character):
    def __init__(self, name, abilities, personality, type, health, strength, 
                 standing_image=None, running_images=None, attacking_images=None):
        
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image,
                         running_images=running_images,
                         attacking_images=attacking_images)
        self.name = "Regular Enemy"
        self.abilities = ["attack"]
        self.personality = "hostile"
        self.type = "regular_enemy"
        self.health = 50
        self.strength = 20
        self.standing_image = standing_image if standing_image else "characters/images/viking.png"
        self.running_images = running_images if running_images else []
        self.attacking_images = attacking_images if attacking_images else []
