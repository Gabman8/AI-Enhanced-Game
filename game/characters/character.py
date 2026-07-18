class Character:

    def __init__(
            self,
            name,
            abilities,
            personality,
            type,
            health,
            strength,
            standing_image=None,
            running_images=None,
            attacking_images=None,
            death_images=None,
            x=0,
            y=0,
            speed=220,
            running=False,
            jumping=False
    ):

        # Información
        self.name = name
        self.type = type
        self.abilities = abilities
        self.personality = personality

        # Estadísticas
        self.health = health
        self.max_health = health
        self.strength = strength

        # Posición
        self.x = x
        self.y = y
        self.speed = speed

        # Estados
        self.running = running
        self.jumping = jumping
        self.attacking = False
        self.dead = False
        self.facing_right = True

        # Animación
        self.animation_state = "idle"
        self.animation_frame = 0
        self.animation_timer = 0

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
    # IMÁGENES
    #########################################################

    def _as_frame_list(self, images):

        if images is None:
            return []

        if isinstance(images, (list, tuple)):
            return list(images)

        return [images]

    #########################################################
    # MOVIMIENTO
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
    # COMBATE
    #########################################################

    def attack(self):

        if self.dead:
            return

        if self.attacking:
            return

        self.attacking = True
        self.set_animation("attack")

    def receive_damage(self, damage):

        if self.dead:
            return

        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):

        self.dead = True
        self.running = False
        self.attacking = False
        self.set_animation("death")

    #########################################################
    # IA (solo ejecuta acciones)
    #########################################################

    def perform_action(self, action, delta_time):

        if action == "MOVE_LEFT":
            self.move_left(delta_time)

        elif action == "MOVE_RIGHT":
            self.move_right(delta_time)

        elif action == "ATTACK":
            self.attack()

        elif action == "IDLE":
            self.stop()

        elif action == "DIE":
            self.die()

    #########################################################
    # ANIMACIONES
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
    # UTILIDADES
    #########################################################

    def distance_to(self, character):
        return abs(self.x - character.x)

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