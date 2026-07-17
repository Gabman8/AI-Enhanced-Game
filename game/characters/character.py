class Character:
    def __init__(self, name, abilities, personality, type, health, strength,
                 standing_image=None, walking_image=None, attacking_image=None,
                 running_images=None, attacking_images=None,
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
        self.running_images = self._as_frame_list(running_images if running_images is not None else walking_image)
        self.attacking_images = self._as_frame_list(attacking_images if attacking_images is not None else attacking_image)
        self.x = x
        self.y = y
        self.speed = speed
        self.running = running
        self.jumping = jumping
        self.attacking = False
        self.facing_right = True
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_fps = {
            "idle": 1,
            "running": 12,
            "attack": 14,
        }

    def _as_frame_list(self, images):
        if images is None or images is Ellipsis:
            return []
        if isinstance(images, (list, tuple)):
            return list(images)
        return [images]

    def set_animation(self, state):
        if state == self.animation_state:
            return
        self.animation_state = state
        self.animation_frame = 0
        self.animation_timer = 0

    def start_attack(self):
        if not self.attacking:
            self.attacking = True
            self.set_animation("attack")

    def update_animation(self, delta_time):
        frames = self.get_animation_frames()
        if not frames:
            return

        frame_duration = 1 / self.animation_fps.get(self.animation_state, 10)
        self.animation_timer += delta_time

        while self.animation_timer >= frame_duration:
            self.animation_timer -= frame_duration
            self.animation_frame += 1

            if self.animation_state == "attack" and self.animation_frame >= len(frames):
                self.attacking = False
                self.set_animation("idle")
                return

            self.animation_frame %= len(frames)

    def get_animation_frames(self):
        if self.animation_state == "attack" and self.attacking_images:
            return self.attacking_images
        if self.animation_state == "running" and self.running_images:
            return self.running_images
        if self.standing_image is not None:
            return [self.standing_image]
        return []

    def get_current_image(self):
        frames = self.get_animation_frames()
        if not frames:
            return None
        return frames[min(self.animation_frame, len(frames) - 1)]

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
    def set_attacking(self, attacking):
        self.attacking = attacking


    
    
