import random
from pathlib import Path
import pandas as pd
import pygame
from levels.generate_characters import get_main_character
from AI.LLM.dialoge_generator import DialogueContext
from screens.dialogue_box import DialogueBox

GAME_ROOT = Path(__file__).resolve().parent.parent

class Game:
    ATTACK_DISTANCE = 200
    SPAWN_INTERVAL = 5.0            
    SPAWN_INTERVAL_VARIANCE = 0.6    
    SPAWN_OFFSCREEN_MARGIN = 150     
    SCREEN_ENTRY_MARGIN = 150        

    def __init__(
            self,
            game,
            running,
            screen,
            enemies,
            background_image,
            delta_time,
            direction,
            decision_manager,
            dialogue_generator_async
    ):  

        self.dialogue_box = DialogueBox()
        self.game = game
        self.running_game = running
        self.screen = screen
        self.decision_manager = decision_manager
        self.dialogue_generator_async = dialogue_generator_async
        self.main_character = get_main_character()
        self.enemies = enemies
        self.level_over = False
        self.background_image = background_image
        self._prepared_background_source = None
        self._prepared_background = None
        self.delta_time = delta_time
        self.direction = direction
        self.jump_velocity = 700
        self.gravity = 1000
        self.ground_y = self.screen.get_height() - 520
        self.auto_mode = False
        #DIALOGUE
        self._prepared_dialogue_box = None
        self._dialogue_font = None
        self._emotion_font = None
        self._health_font = None

        
        if self.main_character is not None:
            self.main_character.y = self.ground_y
        self._spawn_queue = list(self.enemies)
        self._spawn_timer = self._roll_spawn_delay()

        for enemy in self.enemies:
            enemy.y = self.ground_y
            enemy.spawned = False
            enemy.entered_screen = False

    ##################################################
    # SPAWN DE ENEMIGOS
    ##################################################

    def _roll_spawn_delay(self):
        return self.SPAWN_INTERVAL + random.uniform(
            -self.SPAWN_INTERVAL_VARIANCE,
            self.SPAWN_INTERVAL_VARIANCE,
        )

    def _update_spawns(self):
        if not self._spawn_queue:
            return

        self._spawn_timer -= self.delta_time
        if self._spawn_timer <= 0:
            enemy = self._spawn_queue.pop(0)
            self._spawn_enemy(enemy)
            self._spawn_timer = self._roll_spawn_delay()

    def _spawn_enemy(self, enemy):
        # Aparece justo fuera del borde derecho de la pantalla/background,
        # no en mitad de la pantalla.
        enemy.x = self.screen.get_width() + self.SPAWN_OFFSCREEN_MARGIN
        enemy.y = self.ground_y
        enemy.spawned = True
        enemy.entered_screen = False
        enemy.facing_right = False
        enemy.set_running(True)

    def _update_entering_enemy(self, enemy):
        """Enemigo ya soltado pero todavía corriendo hacia dentro de pantalla.
        Mientras tanto no participa en la IA ni en el combate."""
        entry_x = self.screen.get_width() - self.SCREEN_ENTRY_MARGIN
        enemy.move_left(self.delta_time)

        if enemy.x <= entry_x:
            enemy.entered_screen = True
            enemy.decide_action = True  # que la IA tome el control ya mismo

    ##################################################
    # SCREEN LIMITS
    ##################################################

    def _character_width(self, character):
        image = character.get_current_image()
        return image.get_width() if image is not None else 100

    def _clamp_to_screen(self, character):
        min_x = 0
        max_x = self.screen.get_width() - self._character_width(character)
        character.x = max(min_x, min(character.x, max_x))

    ##################################################
    # BACKGROUND
    ##################################################
    def _resolve_asset_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return path
        game_relative = GAME_ROOT / path

        if game_relative.exists():
            return game_relative

        return Path.cwd() / path

    def _prepare_background(self, background):

        if (
                background == self._prepared_background_source
                and self._prepared_background is not None
        ):
            return self._prepared_background

        if isinstance(background, (str, Path)):
            background_path = self._resolve_asset_path(background)

            background = self.game.image.load(
                str(background_path)
            ).convert()

        self._prepared_background_source = background

        self._prepared_background = pygame.transform.scale(
            background,
            self.screen.get_size()
        )

        return self._prepared_background

    ##################################################
    # INPUT
    ##################################################

    def handle_event(self, event):
        if event is None:
            return

        if event.type == self.game.KEYDOWN:

            if event.key == self.game.K_SPACE:

                if (
                        not self.main_character.jumping
                        and self.main_character.y >= self.ground_y - 1
                ):

                    self.main_character.set_jumping(True)
                    self.vertical_velocity = -560

            elif event.key == self.game.K_j:
                self.main_character.attack()

        if (
                event.type == self.game.MOUSEBUTTONDOWN
                and event.button == 1
        ):
            self.main_character.attack()

        
    ##################################################
    # COLLISION
    ##################################################
    def _resolve_collision(self, first, second):
        rect1 = first.get_body_rect()
        rect2 = second.get_body_rect()
        if not rect1.colliderect(rect2):
            return
        overlap = rect1.clip(rect2)
        if rect1.centerx < rect2.centerx:
            first.x -= overlap.width / 2
            second.x += overlap.width / 2
        else:
            first.x += overlap.width / 2
            second.x -= overlap.width / 2
    ##################################################
    # PLAYER
    ##################################################
    def _update_main_character_state(self, keys):
        if self.auto_mode:
            self.evaluate_action()
        else:
            self._poll_dialogue(self.main_character)
            moving_left = keys[self.game.K_a]
            moving_right = keys[self.game.K_d]

            wants_run = (
                    keys[self.game.K_LSHIFT]
                    or keys[self.game.K_RSHIFT]
            )
            self.main_character.set_running(False)
            for enemy in self.enemies:
                if not enemy.spawned:
                    continue
                if enemy.dead:
                    continue
                self._try_hit(
                    enemy,
                    self.main_character
                )
            if moving_right and not moving_left:
                if wants_run:
                    self.main_character.set_speed(self.main_character.sprinting_speed)
                else:
                    self.main_character.set_speed(self.main_character.regular_speed)
                self.main_character.move_right(self.delta_time)
                self.main_character.facing_right = True
                self.main_character.set_running(True)

            elif moving_left and not moving_right:
                if wants_run:
                    self.main_character.set_speed(self.main_character.sprinting_speed)
                else:
                    self.main_character.set_speed(self.main_character.regular_speed)
                self.main_character.move_left(self.delta_time)
                self.main_character.facing_right = False
                self.main_character.set_running(True)
            else:
                self.main_character.stop()

    def _update_jump(self):

        if not self.main_character.jumping:
            return

        self.main_character.y += (
                self.vertical_velocity * self.delta_time
        )

        self.vertical_velocity += (
                self.gravity * self.delta_time
        )

        if self.main_character.y >= self.ground_y:

            self.main_character.y = self.ground_y
            self.main_character.set_jumping(False)
            self.vertical_velocity = 0

    ##################################################
    # ACTIONS
    ##################################################

    def _predict_action(self, character):
        distance = character.distance_to(self.main_character)
        features = {
            "enemy_type": character.type,
            "enemy_personality": character.personality,
            "enemy_emotion": character.emotion,
            "enemy_health": character.health,
            "enemy_strength": character.strength,
            "enemy_speed": character.speed,
            "enemy_running": character.running,
            "enemy_jumping": character.jumping,
            "enemy_attacking": character.attacking,
            "enemy_dead": character.dead,
            "enemy_facing_right": character.facing_right,
            "enemy_animation_state": character.animation_state,
            "enemy_anger": character.anger,
            "enemy_fear": character.fear,
            "enemy_confidence": character.confidence,
            "enemy_last_action": character.last_action,
            "enemy_times_hit": character.times_hit,
            "enemy_times_attack": character.times_attack,
            "player_health": self.main_character.health,
            "player_strength": self.main_character.strength,
            "player_running": self.main_character.running,
            "player_jumping": self.main_character.jumping,
            "player_attacking": self.main_character.attacking,
            "player_dead": self.main_character.dead,
            "player_facing_right": self.main_character.facing_right,
            "player_animation_state": self.main_character.animation_state,
            "distance": distance,
            "player_is_right": self.main_character.facing_right,
        }

        prediction = self.decision_manager.model.predict(features)
        decision = prediction.decision
        character.emotion = prediction.emotion
        character.calculate_emotions()
        return decision
    def _generate_dialogue(self, character, category=None):
        ctx = DialogueContext(
            enemy_type=character.type,
            personality=character.personality,
            anger=character.anger,
            fear=character.fear,
            confidence=character.confidence,
            category=category,
        )
        self.dialogue_generator_async.request(character.id, ctx)

    def _poll_dialogue(self, character):
        line = self.dialogue_generator_async.poll(character.id)
        if line:
            character.current_line = line
            character.show_dialogue = True
            character.line_timer = 3
    def _execute_action(self, character, action):

        if action == "MOVE_RIGHT":

            character.move_right(
                self.delta_time
            )

            character.facing_right = True
            character.set_running(True)
            character.last_action = action

        elif action == "MOVE_LEFT":

            character.move_left(
                self.delta_time
            )

            character.facing_right = False
            character.set_running(True)
            character.last_action = action

        elif action == "ATTACK":
            if not character.attacking:
                body = character.get_body_rect()
                player = self.main_character.get_body_rect()
                if abs(body.centerx - player.centerx) < 90:
                    character.attack()
            character.set_running(False)

            character.last_action = action

    def _update_enemies(self):
        self.evaluate_action(self.main_character)

    def evaluate_action(self, agresor=None):
        # CAMBIO: primero se procesa la cola de spawn
        self._update_spawns()

        for enemy in self.enemies:

            # CAMBIO: todavía no le toca aparecer -> ni se procesa ni se dibuja
            if not enemy.spawned:
                continue

            # CAMBIO: está corriendo hacia dentro de pantalla -> no participa
            # en IA/combate todavía, solo se mueve en línea recta hacia dentro
            if not enemy.entered_screen:
                self._update_entering_enemy(enemy)
                enemy.update_animation(self.delta_time)
                continue

            if agresor == self.main_character:
                 reciever = enemy
            else:
                reciever = self.main_character
                
            self._poll_dialogue(reciever)
            self._try_hit(
                agresor,
                reciever
            )
            reciever.decision_timer += self.delta_time
            if reciever.decision_timer >= enemy.decision_interval:
                reciever.decide_action = True
                reciever.decision_timer = 0
            if reciever.decide_action:
                self._generate_dialogue(reciever)
                reciever.current_action = self._predict_action(reciever)
                reciever.decide_action = False
            self._execute_action(
                reciever,
                reciever.current_action
            )

            # CAMBIO: una vez dentro, no puede volver a salir de pantalla
            if reciever is not self.main_character:
                self._clamp_to_screen(reciever)

            reciever.update_animation(self.delta_time)
    def _try_hit(self, attacker, victim):
        if not attacker.attacking:
            return
        if attacker.damage_done:
            return
        if attacker.attack_animation_timer < attacker.attack_duration * 0.45:
            return
        attack = attacker.get_attack_rect()
        body = victim.get_body_rect()
        if attack.colliderect(body):
            victim.receive_damage(attacker.punching_damage)
            attacker.damage_done = True
    ##################################################
    # DRAW
    ##################################################
    def _get_font(self, attr, size, bold=True):
        font = getattr(self, attr)
        if font is None:
            font = self.game.font.SysFont("Courier", size, bold=bold)
            setattr(self, attr, font)
        return font

    def _draw_character(self, character):

        image = character.get_current_image()

        if image is None:
            return

        if not character.facing_right:

            image = self.game.transform.flip(
                image,
                True,
                False
            )

        self.screen.blit(
            image,
            (character.x, character.y)
        )

    def _health_ratio(self, character):
        if not character.max_health:
            return 0
        return max(0, character.health) / character.max_health

    def _health_color(self, ratio):
        if ratio > 0.5:
            return (0, 200, 0)
        if ratio > 0.25:
            return (230, 200, 0)
        return (200, 0, 0)

    def _draw_health_bar(self, x, y, width, height, ratio, border=2):
        # borde
        self.game.draw.rect(
            self.screen, (20, 20, 20),
            (x - border, y - border, width + border * 2, height + border * 2)
        )
        # fondo vacío
        self.game.draw.rect(self.screen, (90, 0, 0), (x, y, width, height))
        # relleno según vida
        fill_width = int(width * ratio)
        if fill_width > 0:
            self.game.draw.rect(
                self.screen, self._health_color(ratio),
                (x, y, fill_width, height)
            )

    def _draw_main_character_health_bar(self):
        width, height = 420, 38
        margin = 28
        x = margin
        y = self.screen.get_height() - margin - height

        ratio = self._health_ratio(self.main_character)
        self._draw_health_bar(x, y, width, height, ratio, border=3)

        font = self._get_font("_health_font", 20)
        label = f"{max(0, int(self.main_character.health))} / {int(self.main_character.max_health)}"
        text_surface = font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def _draw_enemy_health_bar(self, enemy):
        width, height = 80, 10
        x = enemy.x + (self._character_width(enemy) - width) // 2
        y = enemy.y - 20
        ratio = self._health_ratio(enemy)
        self._draw_health_bar(x, y, width, height, ratio, border=1)

    def _draw_emotion(self, character, anchor_y):
        if not character.show_emotion or not character.emotion:
            return
        font = self._get_font("_emotion_font", 16)
        surface = font.render(character.emotion.capitalize(), True, (255, 230, 0))
        center_x = character.x + self._character_width(character) // 2
        rect = surface.get_rect(midbottom=(center_x, anchor_y))
        self.screen.blit(surface, rect)
    def _draw_enemy_overlay(self, enemy):
        self._draw_enemy_health_bar(enemy)
        self._draw_emotion(
            enemy,
            enemy.y - 24
        )
        self.dialogue_box.draw(
            self.screen,
            enemy
        )
    def _draw_main_character_overlay(self):
        self._draw_main_character_health_bar()
        self._draw_emotion(
            self.main_character,
            self.main_character.y - 10
        )
        self.dialogue_box.draw(
            self.screen,
            self.main_character
        )

    ##################################################
    # GAME LOOP
    ##################################################
    def create_game(self, event, delta_time=None):

        if delta_time is not None:
            self.delta_time = delta_time
        background = self._prepare_background(self.background_image)
        self.screen.blit(background, (0, 0))
        keys = self.game.key.get_pressed()

        self._update_main_character_state(keys)
        self._update_jump()
        self.main_character.update_animation(self.delta_time)
        self.main_character.update_attack(self.delta_time)
        self.main_character.update_status_timers(self.delta_time)

        self._clamp_to_screen(self.main_character)
        self._update_enemies()
        self._draw_character(self.main_character)
        self._draw_main_character_overlay()
        for enemy in self.enemies:

            if not enemy.spawned:
                continue
            self._draw_character(enemy)
            self._draw_enemy_overlay(enemy)
            enemy.update_attack(self.delta_time)
        self.game.display.flip()

        if all(enemy.dead for enemy in self.enemies):
            self.level_over = True

        if self.main_character.dead:
            self.level_over = True