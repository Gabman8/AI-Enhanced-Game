class MainMenu:
    def __init__(self, pygame_module, running, screen, color="Black", font_size=30, font_style="Courier", background_image=None):
        self.pygame = pygame_module
        self.running_game = running
        self.screen = screen
        self.color = color
        self.font_size = font_size
        self.font_style = font_style
        self.background_image = background_image

    def _prepare_background(self):
        if self.background_image is None:
            return None
        if isinstance(self.background_image, str):
            self.background_image = self.pygame.image.load(self.background_image).convert()
        return self.pygame.transform.scale(self.background_image, self.screen.get_size())

    def create_menu(self, event):
        target_screen = self.screen
        background = self._prepare_background()
        if background is not None:
            target_screen.blit(background, (0, 0))
        else:
            target_screen.fill(self.color)

        font = self.pygame.font.SysFont(self.font_style, self.font_size, bold=True)
        start_surface = font.render("Start Game", True, (255, 255, 255))
        quit_surface = font.render("Quit Game", True, (255, 255, 255))

        start_rect = start_surface.get_rect(center=(target_screen.get_width() // 2, target_screen.get_height() // 2 + 20))
        quit_rect = quit_surface.get_rect(center=(target_screen.get_width() // 2, target_screen.get_height() // 2 + 60))

        target_screen.blit(start_surface, start_rect)
        target_screen.blit(quit_surface, quit_rect)
        self.pygame.display.flip()

        if event.type == self.pygame.QUIT:
            self.running_game = False
            return

        