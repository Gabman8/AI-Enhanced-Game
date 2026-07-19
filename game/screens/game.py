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
        self.background_image = background_image or str(DEFAULT_BACKGROUND)
        self._prepared_background_source = None
        self._prepared_background = None 
        self.delta_time = delta_time
        self.direction = direction
        self.move_speed = 420
        self.run_speed = 760
        self.jump_velocity = 700
        self.gravity = 1400
        self.ground_y = self.screen.get_height() - 400
        if self.main_character is not None:
            self.main_character.y = self.ground_y

    def _prepare_background(self, background):
        if background is None:
            return None
        if isinstance(background, str):
            background = self.game.image.load(background).convert()
        return pygame.transform.scale(background, self.screen.get_size())

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

        speed = self.run_speed if wants_run else self.move_speed

        self.main_character.set_running(False)

        if moving_right and not moving_left:

            self.main_character.move_right(self.delta_time)
            self.main_character.facing_right = True
            self.main_character.set_running(True)

        elif moving_left and not moving_right:

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

    def _decide_enemy_action(self, enemy):
        """
        ESTE MÉTODO SERÁ SUSTITUIDO POR EL MODELO IA.
        """
        distance = abs(
            enemy.x - self.main_character.x
        )
        features = pd.DataFrame([{
            "enemy_type": enemy.type,
            "enemy_level": enemy.strength,
            "enemy_state": enemy.animation_state,
            "enemy_direction": int(enemy.facing_right),
            "enemy_speed": enemy.speed,
            "player_distance": distance,
            "player_health": self.main_character.health,
            "player_running": self.main_character.running,
            "player_attacking": self.main_character.attacking,
        }])

        decision = self.decision_manager.model.predict(features)
        print(f"decision {decision}")
        
        if distance <= self.ATTACK_DISTANCE:
            return "ATTACK"

        if enemy.x < self.main_character.x:
            return "MOVE_RIGHT"

        return "MOVE_LEFT"

    def _execute_enemy_action(self, enemy, action):

        if action == "MOVE_RIGHT":

            enemy.move_right(
                self.delta_time
            )

            enemy.facing_right = True
            enemy.set_running(True)

        elif action == "MOVE_LEFT":

            enemy.move_left(
                self.delta_time
            )

            enemy.facing_right = False
            enemy.set_running(True)

        elif action == "ATTACK":

            enemy.set_running(False)

            if not enemy.attacking:
                enemy.attack()

    def _update_enemies(self):

        for enemy in self.enemies:
            distance = abs(
                        enemy.x - self.main_character.x
                    )
            if distance <= self.ATTACK_DISTANCE and self.main_character.attacking:
                enemy.receive_damage(self.main_character.punching_damage)
       
            action = self._decide_enemy_action(enemy)

            self._execute_enemy_action(enemy, action)

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

        pygame_module = self.game
        main_character_image = self.main_character.standing_image
        background = self._prepare_background(self.background_image)
        keys = pygame_module.key.get_pressed()

        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((200, 200, 100))

        self.handle_event(event)

        if keys[pygame_module.K_d] and keys[pygame_module.K_LSHIFT]:
            self.direction = "running_right"
        elif keys[pygame_module.K_d]:
            self.direction = "moving_right"
        elif keys[pygame_module.K_a] and keys[pygame_module.K_LSHIFT]:
            self.direction = "running_left"
        elif keys[pygame_module.K_a]:
            self.direction = "moving_left"
        else:
            self.direction = "idle"

        if self.direction == "moving_right":
            self.main_character.increase_x(self.move_speed * self.delta_time)
        elif self.direction == "moving_left":
            self.main_character.decrease_x(self.move_speed * self.delta_time)
        elif self.direction == "running_right":
            self.main_character.increase_x(self.run_speed * self.delta_time)
        elif self.direction == "running_left":
            self.main_character.decrease_x(self.run_speed * self.delta_time)

        if self.main_character.jumping:
            self.main_character.y += self.jump_velocity * self.delta_time
            self.jump_velocity += self.gravity * self.delta_time
            if self.main_character.y >= self.ground_y:
                self.main_character.y = self.ground_y
                self.main_character.set_jumping(False)
                self.jump_velocity = 0

        self.screen.blit(main_character_image, (self.main_character.x, self.main_character.y))
        pygame_module.display.flip()
        return self.running_game
