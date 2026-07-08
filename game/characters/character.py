class Character:
    def __init__(self, name, abilities, personality, type, health, strength,
                 standing_image=None, walking_image=None, attacking_image=None,
                 x=0, y=0, speed=200, running=False, jumping=False):
        self.name = name
        self.abilities = abilities
        self.personality = personality
        self.type = type
        self.health = health
        self.strength = strength
        self.standing_image = standing_image
        self.walking_image = walking_image
        self.attacking_image = attacking_image
        self.x = x
        self.y = y
        self.speed = speed
        self.running = running
        self.jumping = jumping

    def set_health(self, health):
        self.health = health
    def set_strength(self, strength):
        self.strength = strength 
    def set_abilities(self, abilities):
        self.abilities = abilities
    def increase_x(self, number):
        self.x += number
    def increase_y(self, number):
        self.y += number
    def decrease_x(self, number):
        self.x -= number
    def decrease_y(self, number):
        self.y -= number
    def set_speed(self, speed):
        self.speed = speed
    def set_running(self, running):
        self.running = running
    def set_jumping(self, jumping):
        self.jumping = jumping
    


    
    