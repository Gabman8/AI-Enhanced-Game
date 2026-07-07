class MainMenu:
    def __init__(self, pygame_module, screen, color="Black", font_size=30, font_style="Courier", background_image=None):
        self.pygame = pygame_module
        self.screen = screen
        self.color = color
        self.font_size = font_size
        self.font_style = font_style
        self.background_image = background_image

    def create_menu(self, screen=None):
        target_screen = screen or self.screen

        if self.background_image:
            target_screen.blit(self.background_image, (0, 0))
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

        