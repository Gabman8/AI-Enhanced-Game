class FinishScreen:
    # Initialize the FinishScreen instance with its runtime state.
    def __init__(self, pygame, screen, font_size=140, subtitle_font_size=36, font_name="Courier"):
        self.pygame = pygame
        self.screen = screen
        self.font = pygame.font.SysFont(font_name, font_size, bold=True)
        self.subtitle_font = pygame.font.SysFont(font_name, subtitle_font_size, bold=False)

    # Create finish screen for the current workflow.
    def create_finish_screen(
        self,
        event,
        title,
        subtitle,
        accent=(200, 40, 40),
    ):
        """Dibuja la pantalla de muerte/victoria. Devuelve True si el jugador
        ha hecho click (para indicar que hay que reiniciar)."""

        self.screen.fill((0, 0, 0))

        title_surface = self.font.render(title, True, accent)
        subtitle_surface = self.subtitle_font.render(subtitle, True, accent)

        title_rect = title_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        subtitle_rect = subtitle_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 120)
        )

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)
        self.pygame.display.flip()

        clicked = (
            event is not None
            and event.type == self.pygame.MOUSEBUTTONUP
            and event.button == 1
        )
        return clicked
