
from characters.character import Character

class RegularEnemy(Character):
    def __init__(self):   
        super().__init__(
            name = "Regular Enemy",
            abilities = ["attack"],
            personality = "hostile",
            type = "regular_enemy",
            health = 50,
            strength = 20,
            standing_image = [],
            running_images =  [],
            attacking_images =  []
        )
        
