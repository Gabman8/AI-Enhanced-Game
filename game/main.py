import pygame
from levels.generate_map import generate_map
from levels.generate_characters import generate_characters
from screens.main_menu import MainMenu
from screens.game import Game

pygame.init()
WIDTH, HEIGHT = 2048, 1200
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.FULLSCREEN para poner panta
RESOLUTION = SCREEN.get_size()
MAP_DATA = generate_map("coast-landscape", (100, 100), ["trees", "rocks"], ["goblin", "troll"])
CHARACTERS_DATA = generate_characters(pygame)


#for multiple character this code will be usefull
#characters = pygame.Surface((64, 64), pygame.SRCALPHA)
#characters.blit(main_character_image, (0, 0))
#characters.blit(main_character_image, (0, 0))
running = True;
clock = pygame.time.Clock()
state = "Menu"

main_menu = MainMenu(
    pygame,
    SCREEN,
    "Red",
    30,
    "Courier"
)
background_image = MAP_DATA["image"]
game = Game(
    pygame, 
    SCREEN, 
    CHARACTERS_DATA,
    RESOLUTION,
    background_image
)


while running:
    for event in pygame.event.get():
        if state == "Menu":
            main_menu.create_menu(SCREEN)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                state = "Game"
        elif state == "Game":
            game.create_game()

pygame.quit()




