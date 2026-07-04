
from game.characters.character import Character

class Friend(Character):
    def __init__(self, name, abilities, personality, type, health, strength):
        super().__init__(name, abilities, personality, type, health, strength)
        self.name = "friend"
        self.abilities = ["help"]
        self.personality = "friendly"
        self.type = "friend"
        self.health = 100
        self.strength = 70