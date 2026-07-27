from pathlib import Path


GAME_ROOT = Path(__file__).resolve().parent.parent


class MainMenu:
    def __init__(self, pygame_module, running, screen, color="Black", font_size=30, font_style="Courier", background_image=None):
        self.pygame = pygame_module
        self.running_game = running
        self.screen = screen
        self.color = color
        self.font_size = font_size
        self.font_style = font_style
        self.background_image = background_image
        self._background_cache = None
        self._background_cache_key = None
        self._title_font = self.pygame.font.SysFont("Georgia", 84, bold=True)
        self._subtitle_font = self.pygame.font.SysFont("Georgia", 26, bold=True)
        self._button_font = self.pygame.font.SysFont("Verdana", 28, bold=True)
        self._body_font = self.pygame.font.SysFont("Verdana", 22)
        self._small_font = self.pygame.font.SysFont("Verdana", 18)
        self._button_rects = {}

    def set_background_image(self, background_image):
        self.background_image = background_image
        self._background_cache = None
        self._background_cache_key = None

    def _prepare_background(self):
        if self.background_image is None:
            return None

        if self.background_image == self._background_cache_key and self._background_cache is not None:
            return self._background_cache

        background_path = Path(self.background_image)
        if not background_path.is_absolute():
            background_path = GAME_ROOT / background_path

        background = self.pygame.image.load(str(background_path)).convert()
        background = self.pygame.transform.smoothscale(background, self.screen.get_size())

        self._background_cache = background
        self._background_cache_key = self.background_image
        return background

    def _draw_button(self, label, rect, hovered, accent, secondary=False):
        surface = self.pygame.Surface(rect.size, self.pygame.SRCALPHA)
        fill = (*accent, 245 if hovered else 210)
        border = (255, 255, 255, 235 if hovered else 180)
        if secondary:
            fill = (20, 26, 38, 220 if hovered else 185)
            border = (*accent, 240 if hovered else 185)

        self.pygame.draw.rect(surface, fill, surface.get_rect(), border_radius=22)
        self.pygame.draw.rect(surface, border, surface.get_rect(), width=3, border_radius=22)
        self.screen.blit(surface, rect.topleft)

        text_surface = self._button_font.render(label, True, (249, 249, 249))
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _draw_controls_panel(self, panel_rect):
        overlay = self.pygame.Surface(panel_rect.size, self.pygame.SRCALPHA)
        self.pygame.draw.rect(overlay, (13, 18, 28, 220), overlay.get_rect(), border_radius=28)
        self.pygame.draw.rect(overlay, (255, 255, 255, 45), overlay.get_rect(), width=2, border_radius=28)
        self.screen.blit(overlay, panel_rect.topleft)

        title = self._subtitle_font.render("Controls", True, (255, 224, 160))
        self.screen.blit(title, (panel_rect.x + 24, panel_rect.y + 20))

        controls = [
            "A / D  Move left and right",
            "Shift  Sprint",
            "Space  Jump",
            "J or Left Click  Attack",
            "M  Open pause menu",
            "Esc  Quit from menu",
        ]
        for index, line in enumerate(controls):
            text = self._body_font.render(line, True, (235, 239, 245))
            self.screen.blit(text, (panel_rect.x + 24, panel_rect.y + 70 + index * 34))

    def create_menu(self, event, has_active_game=False, paused=False):
        action = None
        background = self._prepare_background()
        if background is not None:
            self.screen.blit(background, (0, 0))
        else:
            self.screen.fill((18, 22, 30))

        wash = self.pygame.Surface(self.screen.get_size(), self.pygame.SRCALPHA)
        wash.fill((5, 9, 16, 180))
        self.screen.blit(wash, (0, 0))

        left_panel = self.pygame.Rect(120, 110, 860, 860)
        right_panel = self.pygame.Rect(1080, 170, 760, 520)
        for panel_rect, alpha in ((left_panel, 210), (right_panel, 190)):
            panel = self.pygame.Surface(panel_rect.size, self.pygame.SRCALPHA)
            self.pygame.draw.rect(panel, (9, 14, 24, alpha), panel.get_rect(), border_radius=32)
            self.pygame.draw.rect(panel, (255, 255, 255, 36), panel.get_rect(), width=2, border_radius=32)
            self.screen.blit(panel, panel_rect.topleft)

        title = self._title_font.render("Comando", True, (248, 233, 190))
        subtitle_text = "Pause Menu" if paused else "Street fight survival"
        subtitle = self._subtitle_font.render(subtitle_text, True, (220, 228, 235))
        self.screen.blit(title, (left_panel.x + 40, left_panel.y + 40))
        self.screen.blit(subtitle, (left_panel.x + 44, left_panel.y + 138))

        description_lines = [
            "Fight through enemy waves, stay alive, and clear the street.",
            "Use the pause menu anytime with M, then resume or restart your run.",
        ]
        for index, line in enumerate(description_lines):
            text = self._body_font.render(line, True, (225, 231, 239))
            self.screen.blit(text, (left_panel.x + 44, left_panel.y + 205 + index * 34))

        primary_label = "Resume Game" if has_active_game else "Start Game"
        secondary_label = "New Run" if has_active_game else "Quit Game"
        tertiary_label = "Quit Game" if has_active_game else None
        actions = [("primary", primary_label, "resume" if has_active_game else "start")]
        if has_active_game:
            actions.append(("secondary", secondary_label, "restart"))
            actions.append(("tertiary", tertiary_label, "quit"))
        else:
            actions.append(("secondary", secondary_label, "quit"))

        accent = (180, 72, 40)
        self._button_rects = {}
        mouse_pos = self.pygame.mouse.get_pos()
        button_y = left_panel.y + 340
        for name, label, button_action in actions:
            rect = self.pygame.Rect(left_panel.x + 44, button_y, 330, 72)
            hovered = rect.collidepoint(mouse_pos)
            self._draw_button(label, rect, hovered, accent, secondary=name != "primary")
            self._button_rects[button_action] = rect
            button_y += 92

        tip = self._small_font.render("Click a button or press Enter to continue.", True, (205, 214, 224))
        self.screen.blit(tip, (left_panel.x + 44, left_panel.bottom - 60))

        self._draw_controls_panel(right_panel)
        self.pygame.display.flip()

        if event is None:
            return None

        if event.type == self.pygame.KEYDOWN:
            if event.key == self.pygame.K_ESCAPE:
                return "quit"
            if event.key in (self.pygame.K_RETURN, self.pygame.K_SPACE):
                return "resume" if has_active_game else "start"
            if event.key == self.pygame.K_r and has_active_game:
                return "restart"

        if event.type == self.pygame.MOUSEBUTTONUP and event.button == 1:
            for button_action, rect in self._button_rects.items():
                if rect.collidepoint(event.pos):
                    action = button_action
                    break

        return action
