
from game.characters.character import Character

class Girlfriend(Character):
    def __init__(self, name, abilities, personality, type, health, strength, standing_image, running_images, attacking_images):
        super().__init__(name, abilities, personality, type, health, 
                         strength, standing_image,
                         running_images=running_images,
                         attacking_images=attacking_images)
        self.name = "Girlfriend"
        self.abilities = ["friendly", "loving"]
        self.personality = "loving"
        self.type = "girlfriend"
        self.health = 50
        self.strength = 20
