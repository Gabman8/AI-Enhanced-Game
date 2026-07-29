import uuid
import pygame
class Character:

    # Initialize the Character instance with its runtime state.
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
            jumping=False,
            display_name=None,
            dialogue_style=None,
            attack_cooldown=0.3,
            decision_interval=0.8,
            never_flee=False,
            persists_on_death=False,
            intro_line=None,
            entrance_announcement=None,
            death_line=None,
    ):
        self.id = uuid.uuid4()
        # Información
        self.name = name
        self.display_name = display_name or name
        self.type = type
        self.abilities = abilities
        self.personality = personality
        self.dialogue_style = dialogue_style or personality
        self.emotion = emotion
        self.last_action = None
        self.anger = anger
        self.fear = fear
        self.times_hit = 0
        self.times_attack = 0
        self.hits_landed = 0
        self.damage_received = 0.0
        self.confidence = confidence
        self.decide_action = False
        self.never_flee = never_flee
        self.persists_on_death = persists_on_death
        self.intro_line = intro_line
        self.entrance_announcement = entrance_announcement
        self.death_line = death_line
        self.action_lock_timer = 0
        self.is_final_boss = type == "final_boss"

        self.current_action = "IDLE"
        self.decision_timer = 0
        self.decision_interval = decision_interval
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
        self.death_timer = 0  # Timer to fade out dead enemies
        self.should_remove = False  # Flag to remove dead enemies

        # Animación
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0

        #Dialogo
        self.current_line = None
        self.line_timer = 0
        self.show_dialogue = False

        # COMBATE
        self.attack_cooldown = attack_cooldown
        self.attack_timer = 0

        self.attack_duration = 0.2
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

    # Handle as frame list for the current workflow.
    def _as_frame_list(self, images):

        if images is None:
            return []

        if isinstance(images, (list, tuple)):
            return list(images)

        return [images]
    # Update status timers for the current frame or state.
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

        if self.action_lock_timer > 0:
            self.action_lock_timer = max(0, self.action_lock_timer - delta)
        
        # Death timer: enemies fade out after 2 seconds
        if self.dead:
            self.death_timer += delta
            if not self.persists_on_death and self.death_timer > 2.0:
                self.should_remove = True

    #########################################################
    # MOVEMENT
    #########################################################

    # Move left according to the current rules.
    def move_left(self, delta_time):

        if self.dead:
            return

        self.x -= self.speed * delta_time
        self.running = True
        self.facing_right = False

        if not self.attacking:
            self.set_animation("running")

    # Move right according to the current rules.
    def move_right(self, delta_time):

        if self.dead:
            return

        self.x += self.speed * delta_time
        self.running = True
        self.facing_right = True

        if not self.attacking:
            self.set_animation("running")

    # Handle stop for the current workflow.
    def stop(self):

        if self.dead:
            return

        self.running = False

        if not self.attacking:
            self.set_animation("idle")

    #########################################################
    # COMBAT
    #########################################################

    # Handle attack for the current workflow.
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

    # Handle receive damage for the current workflow.
    def receive_damage(self, damage):
        if self.dead:
            return
        self.times_hit += 1
        self.damage_received += float(damage)

        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.die()

    # Handle die for the current workflow.
    def die(self):

        if self.dead:
            return
        self.dead = True
        self.running = False
        self.attacking = False
        self.falling = True
        self.vertical_velocity = 0
        self.death_timer = 0
        # Lock facing direction at death — don't flip while falling
        self._death_facing_right = self.facing_right
        if self.death_line:
            self.current_line = self.death_line
            self.show_dialogue = True
            self.line_timer = 2.4
        self.set_animation("death")
        
    # Update physics for the current frame or state.
    def update_physics(self, delta_time, ground_y):
        if self.falling:
            self.vertical_velocity += 1400 * delta_time
            self.y += self.vertical_velocity * delta_time

            if self.y >= ground_y:
                self.y = ground_y
                self.falling = False
    # Update attack for the current frame or state.
    def update_attack(self, delta):
        if self.attack_timer > 0:
            self.attack_timer = max(
                0,
                self.attack_timer - delta
            )
    #########################################################
    # ANIMATIONS
    #########################################################

    # Set animation on the current object.
    def set_animation(self, state):

        if state == self.animation_state:
            return

        self.animation_state = state
        self.animation_frame = 0
        self.animation_timer = 0
 
    # Return animation frames for the current flow.
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

    # Update animation for the current frame or state.
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
    # Return current image for the current flow.
    def get_current_image(self):
        frames = self.get_animation_frames()

        if not frames:
            return self.standing_image

        return frames[
        min(
            self.animation_frame,
            len(frames) - 1
        )
    ]
    #########################################################
    # EMOTIONS
    #########################################################
    # Calculate emotions from the current values.
    def calculate_emotions(self):
        """Apply emotion-based adjustments to emotional stats."""
        self.show_emotion = True
        self.emotion_timer = 1.0
        
        # Reset all to baseline then adjust based on emotion
        base_anger = 0.3
        base_fear = 0.2
        base_confidence = 0.5
        
        if self.emotion == "calm":
            self.anger = base_anger - 0.2
            self.confidence = min(1, base_confidence + 0.2)
            self.fear = base_fear - 0.15
        elif self.emotion == "confident":
            self.anger = base_anger - 0.15
            self.confidence = min(1, base_confidence + 0.35)
            self.fear = base_fear - 0.15
        elif self.emotion == "angry":
            self.anger = min(1, base_anger + 0.4)
            self.confidence = min(1, base_confidence + 0.15)
            self.fear = base_fear - 0.15
        elif self.emotion == "afraid":
            self.anger = base_anger - 0.2
            self.confidence = max(0, base_confidence - 0.35)
            self.fear = min(1, base_fear + 0.5)
        
        # Clamp all to 0-1
        self.anger = max(0, min(1, self.anger))
        self.fear = max(0, min(1, self.fear))
        self.confidence = max(0, min(1, self.confidence))

    #########################################################
    # HITBOX
    #########################################################
    # Return body rect for the current flow.
    def get_body_rect(self):
        image = self.get_current_image()
        if image is None:
            width, height = 100, 150
        else:
            width = image.get_width()
            height = image.get_height()
        margin_x = width * 0.35
        return pygame.Rect(
            self.x + margin_x,
            self.y,
            width - margin_x * 2,
            height
    )
    # Return attack rect for the current flow.
    def get_attack_rect(self):

        body = self.get_body_rect()
        attack_width = 110
        if self.facing_right:
            return pygame.Rect(
                body.right,
                body.y + 18,
                attack_width,
                body.height - 36
            )
        return pygame.Rect(
            body.left - attack_width,
            body.y + 18,
            attack_width,
            body.height - 36
        )
    #########################################################
    # UTILS
    #########################################################

    # Handle distance to for the current workflow.
    def distance_to(self, character):
        return abs(self.x - character.x)
    # Increase emotion by the requested amount.
    def increment_emotion(self,emotion, quantity):
        emotion += quantity
        return emotion
    # Decrease emotion by the requested amount.
    def decrement_emotion(self,emotion, quantity):
        emotion -= quantity
        return emotion
    #########################################################
    # SETTERS
    #########################################################

    # Set health on the current object.
    def set_health(self, health):
        self.health = health

    # Set strength on the current object.
    def set_strength(self, strength):
        self.strength = strength

    # Set speed on the current object.
    def set_speed(self, speed):
        self.speed = speed

    # Set running on the current object.
    def set_running(self, running):
        self.running = running

    # Set jumping on the current object.
    def set_jumping(self, jumping):
        self.jumping = jumping

    # Set attacking on the current object.
    def set_attacking(self, attacking):
        self.attacking = attacking
