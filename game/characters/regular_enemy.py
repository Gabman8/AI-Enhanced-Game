
from game.characters.character import Character

class RegularEnemy(Character):
    def __init__(self, name, abilities, personality, type, health, strength, 
                 standing_image, walking_images, attacking_images):
        
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image, walking_images, 
                         attacking_images)
        self.name = "Regular Enemy"
        self.abilities = ["attack"]
        self.personality = "hostile"
        self.type = "regular_enemy"
        self.health = 50
        self.strength = 20
