import pygame
from levels.generate_level import generate_level
from screens.main_menu import MainMenu
from screens.game import Game

pygame.init()
WIDTH, HEIGHT = 2048, 1200
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Comando")

FPS = 144
DEFAULT_BACKGROUND = "backgrounds/TimesSquare_background.png"
LEVEL = generate_level(pygame)

running = True
state = "Menu"
clock = pygame.time.Clock()
background_image = LEVEL.get("enemies").get("image") or DEFAULT_BACKGROUND
main_menu = MainMenu(
    pygame,
    running,
    SCREEN,
    "Red",
    30,
    "Courier",
    background_image
)
direction = "Static"
game = Game(
    pygame,
    running,
    SCREEN,
    LEVEL.get("enemies"),
    background_image,
    0.5,
    direction,
)
while running:
    delta_time = clock.tick(FPS) / 1000.0
    delta_time = min(delta_time, 0.1)
    event = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if state == "Menu":
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                state = "Game"
        elif state == "Game":
            game.handle_event(event)

    if state == "Menu":
         main_menu.create_menu(event)
    elif state == "Game":
         game.create_game(event, delta_time)
         if game.level_completed:
             state = "Menu"
pygame.quit()




