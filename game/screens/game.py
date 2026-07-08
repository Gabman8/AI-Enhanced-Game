import pygame
from levels.generate_characters import get_main_character


class Game:
    def __init__(self, game, running, screen, characters, background_image, delta_time, direction):
        self.game = game
        self.running_game = running
        self.screen = screen
        self.characters = characters
        self.main_character = get_main_character()
        self.background_image = background_image
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

        if event.type == self.game.KEYDOWN and event.key == self.game.K_SPACE:
            if not self.main_character.jumping and self.main_character.y >= self.ground_y - 1:
                self.main_character.set_jumping(True)
                self.jump_velocity = -560

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
