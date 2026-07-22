import random
from pathlib import Path
import pandas as pd
import pygame
from levels.generate_characters import get_main_character
from AI.LLM.dialoge_generator import DialogueContext

GAME_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKGROUND = GAME_ROOT / "backgrounds" / "TimesSquare_backgdround.png"
DIALOGUE_BOX =  GAME_ROOT / "images" / "utils" / "dialog_box.png"

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
    # LÍMITES DE PANTALLA
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
                distance = self.main_character.distance_to(enemy)
                if distance <= self.ATTACK_DISTANCE and enemy.attacking:
                      self.main_character.receive_damage(enemy.punching_damage)
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
            print(line)
            character.current_line = line
            character.line_timer = 3.0
            character.show_dialogue = True
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

            character.set_running(False)

            if not character.attacking:
                character.attack()
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
            distance = enemy.distance_to(agresor)
            if distance <= self.ATTACK_DISTANCE and agresor.attacking:
                reciever.receive_damage(agresor.punching_damage)
                reciever.decide_action = True
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

    ##################################################
    # DRAW
    ##################################################

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
    def _draw_dialogue_box(self, character, text):

        image = DIALOGUE_BOX
        if image is None:
            return
        image = self.game.transform.flip(
                        image,
                        True,
                        False
                    )
        self.screen.blit(
            image,
            (character.x + 10, character.y + 50)
        )

    ##################################################
    # GAME LOOP
    ##################################################

    def create_game(self, event, delta_time=None):

        if delta_time is not None:
            self.delta_time = delta_time

        background = self._prepare_background(
            self.background_image
        )
        self.screen.blit(background, (0, 0))
        self._draw_character(self.main_character)
        for enemy in self.enemies:
            if enemy.spawned:
                self._draw_character(enemy)

        keys = self.game.key.get_pressed()
        self._update_enemies()
        self._update_main_character_state(keys)
        self._update_jump()

        self.main_character.update_animation(
            self.delta_time
        )

        self.game.display.flip()
        if all(enemy.dead for enemy in self.enemies):
            self.level_over = True
        if self.main_character.dead:
            self.level_over = True
        return self.running_game