from pathlib import Path
import pygame
from levels.generate_characters import get_main_character


GAME_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKGROUND = GAME_ROOT / "backgrounds" / "London_background.png"


class Game:
    def __init__(self, game, running, screen, characters, background_image, delta_time, direction):
        self.game = game
        self.running_game = running
        self.screen = screen
        self.characters = characters
        self.main_character = get_main_character()
        self.background_image = background_image or str(DEFAULT_BACKGROUND)
        self._prepared_background_source = None
        self._prepared_background = None
        self.delta_time = delta_time
        self.direction = direction
        self.move_speed = 420
        self.run_speed = 760
        self.vertical_velocity = 0
        self.gravity = 1400
        self.ground_y = self.screen.get_height() - 400
        if self.main_character is not None:
            self.main_character.y = self.ground_y

    def _resolve_asset_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return path

        game_relative = GAME_ROOT / path
        if game_relative.exists():
            return game_relative

        return Path.cwd() / path

    def _prepare_background(self, background):
        if background is None:
            background = DEFAULT_BACKGROUND

        if background == self._prepared_background_source and self._prepared_background is not None:
            return self._prepared_background

        if isinstance(background, (str, Path)):
            background_path = self._resolve_asset_path(background)
            if not background_path.exists():
                background_path = DEFAULT_BACKGROUND
            background = self.game.image.load(str(background_path)).convert()

        self._prepared_background_source = background
        self._prepared_background = pygame.transform.scale(background, self.screen.get_size())
        return self._prepared_background

    def handle_event(self, event):
        if event is None or self.main_character is None:
            return

        if event.type == self.game.KEYDOWN:
            if event.key == self.game.K_SPACE:
                if not self.main_character.jumping and self.main_character.y >= self.ground_y - 1:
                    self.main_character.set_jumping(True)
                    self.vertical_velocity = -560
            elif event.key == self.game.K_j:
                self.main_character.start_attack()

        if event.type == self.game.MOUSEBUTTONDOWN and event.button == 1:
            self.main_character.start_attack()

    def _update_main_character_state(self, keys):
        moving_left = keys[self.game.K_a]
        moving_right = keys[self.game.K_d]
        wants_run = keys[self.game.K_LSHIFT] or keys[self.game.K_RSHIFT]
        speed = self.run_speed if wants_run else self.move_speed

        self.main_character.set_running(False)
        if moving_right and not moving_left:
            self.main_character.increase_x(speed * self.delta_time)
            self.main_character.facing_right = True
            self.main_character.set_running(True)
            self.direction = "running_right" if wants_run else "moving_right"
        elif moving_left and not moving_right:
            self.main_character.decrease_x(speed * self.delta_time)
            self.main_character.facing_right = False
            self.main_character.set_running(True)
            self.direction = "running_left" if wants_run else "moving_left"
        else:
            self.direction = "idle"

        max_x = self.screen.get_width() - 1
        self.main_character.x = max(0, min(self.main_character.x, max_x))

        if self.main_character.attacking:
            self.main_character.set_animation("attack")
        elif self.main_character.running:
            self.main_character.set_animation("running")
        else:
            self.main_character.set_animation("idle")

    def _update_jump(self):
        if not self.main_character.jumping:
            return

        self.main_character.y += self.vertical_velocity * self.delta_time
        self.vertical_velocity += self.gravity * self.delta_time

        if self.main_character.y >= self.ground_y:
            self.main_character.y = self.ground_y
            self.main_character.set_jumping(False)
            self.vertical_velocity = 0

    def _draw_main_character(self):
        main_character_image = self.main_character.get_current_image()
        if main_character_image is None:
            return

        if not self.main_character.facing_right:
            main_character_image = self.game.transform.flip(main_character_image, True, False)

        self.screen.blit(main_character_image, (self.main_character.x, self.main_character.y))

    def create_game(self, event, delta_time=None):
        if delta_time is not None:
            self.delta_time = delta_time

        background = self._prepare_background(self.background_image)
        self.screen.blit(background, (0, 0))

        if self.main_character is None:
            self.game.display.flip()
            return self.running_game

        keys = self.game.key.get_pressed()
        self._update_main_character_state(keys)
        self._update_jump()
        self.main_character.update_animation(self.delta_time)
        self._draw_main_character()

        self.game.display.flip()
        return self.running_game
