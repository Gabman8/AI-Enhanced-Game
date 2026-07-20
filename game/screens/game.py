from pathlib import Path
import pandas as pd
import pygame
from levels.generate_characters import get_main_character
GAME_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKGROUND = GAME_ROOT / "backgrounds" / "TimesSquare_backgdround.png"


class Game:
    ATTACK_DISTANCE = 200
    def __init__(
            self,
            game,
            running,
            screen,
            enemies,
            background_image,
            delta_time,
            direction,
            decision_manager
    ):
        
        self.game = game
        self.running_game = running
        self.screen = screen
        self.decision_manager = decision_manager
        self.main_character = get_main_character()
        self.enemies = enemies
        self.level_completed = False
        self.background_image = background_image
        self._prepared_background_source = None
        self._prepared_background = None 
        self.delta_time = delta_time
        self.direction = direction
        self.jump_velocity = 700
        self.gravity = 1400
        self.ground_y = self.screen.get_height() - 400
        if self.main_character is not None:
            self.main_character.y = self.ground_y
            # Posición inicial de enemigos
        x = 900

        for enemy in self.enemies:
            enemy.x = x
            enemy.y = self.ground_y
            x += 250

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

        moving_left = keys[self.game.K_a]
        moving_right = keys[self.game.K_d]

        wants_run = (
                keys[self.game.K_LSHIFT]
                or keys[self.game.K_RSHIFT]
        )

        self.main_character.set_running(False)

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
    # ENEMIES
    ##################################################

    def _predict_enemy_action(self, enemy):
    
        distance = enemy.distance_to(self.main_character)
        features = {
            "enemy_type": enemy.type,
            "enemy_personality": enemy.personality,
            "enemy_emotion": enemy.emotion,
            "enemy_health": enemy.health,
            "enemy_strength": enemy.strength,
            "enemy_speed": enemy.speed,
            "enemy_running": enemy.running,
            "enemy_jumping": enemy.jumping,
            "enemy_attacking": enemy.attacking,
            "enemy_dead": enemy.dead,
            "enemy_facing_right": enemy.facing_right,
            "enemy_animation_state": enemy.animation_state,
            "enemy_anger": enemy.anger,
            "enemy_fear": enemy.fear,
            "enemy_confidence": enemy.confidence,
            "enemy_last_action": enemy.last_action,
            "enemy_times_hit": enemy.times_hit,
            "enemy_times_attack": enemy.times_attack,
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
        emotion = prediction.emotion
        print(f"emotion {emotion}")
        return decision

    def _execute_enemy_action(self, enemy, action):

        if action == "MOVE_RIGHT":

            enemy.move_right(
                self.delta_time
            )

            enemy.facing_right = True
            enemy.set_running(True)
            enemy.last_action = action

        elif action == "MOVE_LEFT":

            enemy.move_left(
                self.delta_time
            )

            enemy.facing_right = False
            enemy.set_running(True)
            enemy.last_action = action

        elif action == "ATTACK":

            enemy.set_running(False)

            if not enemy.attacking:
                enemy.attack()
            enemy.last_action = action

    def _update_enemies(self):

        for enemy in self.enemies:
            distance = abs(
                        enemy.x - self.main_character.x
                    )
            if distance <= self.ATTACK_DISTANCE and self.main_character.attacking:
                enemy.receive_damage(self.main_character.punching_damage)
                enemy.decide_action = True
            enemy.decision_timer += self.delta_time

            if enemy.decision_timer >= enemy.decision_interval:
                enemy.decide_action = True
                enemy.decision_timer = 0   
            if enemy.decide_action:
                enemy.current_action = self._predict_enemy_action(enemy)
                enemy.decide_action = False
            self._execute_enemy_action(
                enemy,
                enemy.current_action
            )
            enemy.update_animation(self.delta_time)

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
            self._draw_character(enemy)
    
        keys = self.game.key.get_pressed()

        self._update_main_character_state(keys)
        self._update_jump()

        self.main_character.update_animation(
            self.delta_time
        )
        self._update_enemies()
        self.game.display.flip()
        if all(enemy.dead for enemy in self.enemies):
            self.level_completed = True
        return self.running_game
