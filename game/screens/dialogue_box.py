import pygame

class DialogueBox:

    PADDING = 12
    MAX_WIDTH = 340
    FONT_SIZE = 22

    BACKGROUND = (35, 35, 35)
    BORDER = (240, 240, 240)
    TEXT = (255, 255, 255)

    BORDER_RADIUS = 12

    def __init__(self):

        self.font = pygame.font.SysFont(
            "Arial",
            self.FONT_SIZE,
            bold=True
        )

    #######################################################

    def _wrap_text(self, text):

        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            width = self.font.size(test)[0]
            if width <= self.MAX_WIDTH:
                current = test
            else:
                lines.append(current)
                current = word
        if current:

            lines.append(current)

        return lines

    #######################################################

    def draw(self, screen, character):

        if not character.show_dialogue:
            return
        if not character.current_line:
            return

        lines = self._wrap_text(character.current_line)
        line_height = self.font.get_height()
        width = 0

        for line in lines:
            width = max(width, self.font.size(line)[0])
        width += self.PADDING * 2
        height = len(lines) * line_height + self.PADDING * 2

        x = (
            character.x
            + character.get_current_image().get_width() // 2
            - width // 2
        )
        y = character.y - height - 35
        pygame.draw.rect(
             screen,
            self.BACKGROUND,
            (x, y, width, height),
            border_radius=self.BORDER_RADIUS
        )
        pygame.draw.rect(
            screen,
            self.BORDER,
            (x, y, width, height),
            3,
            border_radius=self.BORDER_RADIUS
        )
        current_y = y + self.PADDING
        for line in lines:
            surface = self.font.render(
                line,
                True,
                self.TEXT
            )
            screen.blit(
                surface,
                (
                    x + self.PADDING,
                    current_y
                )
            )
            current_y += line_height