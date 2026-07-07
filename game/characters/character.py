class Character:
    def __init__(self, name, abilities, personality, type, health, 
                 strength,standing_image, walking_image, attacking_image):
        self.name = name
        self.abilities = abilities
        self.personality = personality
        self.type = type
        self.health = health
        self.strength = strength
        self.standing_image = standing_image
        self.walking_image = walking_image
        self.attacking_image = attacking_image
    def get_name(self):
        return self.name
    def get_abilities(self):
        return self.abilities
    def get_personality(self):
        return self.personality
    def get_type(self):
        return self.type
    def get_health(self):
        return self.health
    def get_strength(self):
        return self.strength
    def set_health(self, health):
        self.health = health
    def set_strength(self, strength):
        self.strength = strength 
    def set_abilities(self, abilities):
        self.abilities = abilities
    
    