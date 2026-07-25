import uuid
import pygame
class Character:

    def __init__(
            self,
            name,
            abilities,
            personality,
            type,
            health,
            strength,
            anger,
            fear,
            confidence,
            emotion=None,
            standing_image=None,
            running_images=None,
            attacking_images=None,
            death_images=None,
            x=0,
            y=0,
            speed=220,
            regular_speed=220,
            sprinting_speed = 450,
            running=False,
            jumping=False
    ):
        self.id = uuid.uuid4()
        # Información
        self.name = name
        self.type = type
        self.abilities = abilities
        self.personality = personality
        self.emotion = emotion
        self.last_action = None
        self.anger = anger
        self.fear = fear
        self.times_hit = 0
        self.times_attack = 0
        self.confidence = confidence
        self.decide_action = False

        self.current_action = "IDLE"
        self.decision_timer = 0
        self.decision_interval = 1.5
        # Estadísticas
        self.health = health
        self.max_health = health
        self.strength = strength
        self.punching_damage = strength * 0.2

        # Posición
        self.x = x
        self.y = y
        self.speed = speed
        self.regular_speed = regular_speed
        self.sprinting_speed = sprinting_speed
        self.vertical_velocity = 0

        # Estados
        self.running = running
        self.falling = False
        self.jumping = jumping
        self.attacking = False
        self.dead = False
        self.facing_right = True
        self.show_emotion = False
        self.emotion_timer = 0

        # Animación
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0

        #Dialogo
        self.current_line = None
        self.line_timer = 0
        self.show_dialogue = False

        # COMBATE
        self.attack_cooldown = 1.0
        self.attack_timer = 0

        self.attack_duration = 0.35
        self.attack_animation_timer = 0

        self.damage_done = False

        # COLISIONES
        self.body_margin = 18

        self.animation_fps = {
            "idle": 1,
            "running": 12,
            "attack": 14,
            "death": 10,
        }

        # Sprites
        self.standing_image = standing_image
        self.running_images = self._as_frame_list(running_images)
        self.attacking_images = self._as_frame_list(attacking_images)
        self.death_images = self._as_frame_list(death_images)

    #########################################################
    # IMAGES
    #########################################################

    def _as_frame_list(self, images):

        if images is None:
            return []

        if isinstance(images, (list, tuple)):
            return list(images)

        return [images]
    def update_status_timers(self, delta):

        if self.show_dialogue:
            self.line_timer -= delta
            if self.line_timer <= 0:
                self.show_dialogue = False
                self.current_line = ""

        if self.show_emotion:
            self.emotion_timer -= delta
            if self.emotion_timer <= 0:
                self.show_emotion = False

    #########################################################
    # MOVEMENT
    #########################################################

    def move_left(self, delta_time):

        if self.dead:
            return

        self.x -= self.speed * delta_time
        self.running = True
        self.facing_right = False

        if not self.attacking:
            self.set_animation("running")

    def move_right(self, delta_time):

        if self.dead:
            return

        self.x += self.speed * delta_time
        self.running = True
        self.facing_right = True

        if not self.attacking:
            self.set_animation("running")

    def stop(self):

        if self.dead:
            return

        self.running = False

        if not self.attacking:
            self.set_animation("idle")

    #########################################################
    # COMBAT
    #########################################################

    def attack(self):
        if self.dead:
            return
        if self.attack_timer > 0:
            return
        self.attacking = True
        self.running = False
        self.attack_timer = self.attack_cooldown
        self.damage_done = False
        self.set_animation("attack")

    def receive_damage(self, damage):
        if self.dead:
            return
        self.times_hit += 1

        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):

        if self.dead:
            return
        self.dead = True
        self.running = False
        self.attacking = False
        self.falling = True
        self.vertical_velocity = 0
        self.set_animation("death")
        
    def update_physics(self, delta_time, ground_y):
        if self.falling:
            self.vertical_velocity += 1400 * delta_time
            self.y += self.vertical_velocity * delta_time

            if self.y >= ground_y:
                self.y = ground_y
                self.falling = False
    def update_attack(self, delta):
        if self.attack_timer > 0:
            self.attack_timer = max(
                0,
                self.attack_timer - delta
            )
    #########################################################
    # ANIMATIONS
    #########################################################

    def set_animation(self, state):

        if state == self.animation_state:
            return

        self.animation_state = state
        self.animation_frame = 0
        self.animation_timer = 0
 
    def get_animation_frames(self):

        if self.animation_state == "attack":
            return self.attacking_images

        if self.animation_state == "running":
            return self.running_images

        if self.animation_state == "death":
            return self.death_images

        if self.standing_image is not None:
            return [self.standing_image]

        return []

    def update_animation(self, delta_time):
        frames = self.get_animation_frames()
        if not frames:
            return

        fps = self.animation_fps.get(
            self.animation_state,
            10
        )
        frame_duration = 1 / fps
        self.animation_timer += delta_time

        while self.animation_timer >= frame_duration:
            self.animation_timer -= frame_duration
            self.animation_frame += 1
            # Ataque termina y vuelve a idle
            if (
                    self.animation_state == "attack"
                    and self.animation_frame >= len(frames)
            ):

                self.attacking = False
                self.damage_done = False
                self.set_animation("idle")
                return
            # Muerte se queda en el último frame
            if self.animation_state == "death":

                if self.animation_frame >= len(frames):
                    self.animation_frame = len(frames) - 1

                return

            self.animation_frame %= len(frames)
    def get_current_image(self):

        frames = self.get_animation_frames()

        if not frames:
            return None

        return frames[
            min(
                self.animation_frame,
                len(frames) - 1
            )
        ]
    #########################################################
    # EMOTIONS
    #########################################################
    def calculate_emotions(self):
        self.show_emotion = True
        self.emotion_timer = 1.0
        if self.emotion == "calm":
            self.anger = self.anger if self.decrement_emotion(self.anger,0.2) <= 0 else self.decrement_emotion(self.anger,0.2)
            self.confidence =self.confidence if self.increment_emotion(self.confidence,0.2) >= 1 else self.increment_emotion(self.confidence,0.2)
            self.fear = self.fear if self.decrement_emotion(self.fear,0.2) <= 0 else self.decrement_emotion(self.fear,0.2)
        elif self.emotion == "confident":
            self.anger = self.anger if self.decrement_emotion(self.anger,0.2) <= 0 else self.decrement_emotion(self.anger,0.2)
            self.confidence = self.confidence if self.increment_emotion(self.confidence,0.3) >= 1 else self.increment_emotion(self.confidence,0.3)
            self.fear = self.fear if self.decrement_emotion(self.fear,0.2) <= 0 else self.decrement_emotion(self.fear,0.2)
        elif self.emotion == "angry":
            self.anger = self.confidence if self.increment_emotion(self.confidence,0.3) >= 1 else self.increment_emotion(self.confidence,0.3)
            self.confidence = self.confidence if self.increment_emotion(self.confidence,0.1) >= 1 else self.increment_emotion(self.confidence,0.1)
            self.fear = self.fear if self.decrement_emotion(self.fear,0.2) <= 0 else self.decrement_emotion(self.fear,0.2)

    #########################################################
    # HITBOX
    #########################################################
    def get_body_rect(self):

        image = self.get_current_image()
        width = image.get_width()
        height = image.get_height()
        margin_x = width * 0.35
        return pygame.Rect(
            self.x + margin_x,
            self.y,
            width - margin_x * 2,
            height
        )
    def get_attack_rect(self):

        body = self.get_body_rect()
        attack_width = 60
        if self.facing_right:
            return pygame.Rect(
                body.right,
                body.y + 25,
                attack_width,
                body.height - 50
            )
        return pygame.Rect(
            body.left - attack_width,
            body.y + 25,
            attack_width,
            body.height - 50
        )
    #########################################################
    # UTILS
    #########################################################

    def distance_to(self, character):
        return abs(self.x - character.x)
    def increment_emotion(self,emotion, quantity):
        emotion += quantity
        return emotion
    def decrement_emotion(self,emotion, quantity):
        emotion -= quantity
        return emotion
    #########################################################
    # SETTERS
    #########################################################

    def set_health(self, health):
        self.health = health

    def set_strength(self, strength):
        self.strength = strength

    def set_speed(self, speed):
        self.speed = speed

    def set_running(self, running):
        self.running = running

    def set_jumping(self, jumping):
        self.jumping = jumping

    def set_attacking(self, attacking):
        self.attacking = attacking
