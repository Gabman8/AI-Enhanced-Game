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
CHARACTERS_DATA = generate_characters()

#for multiple character this code will be usefull
#characters = pygame.Surface((64, 64), pygame.SRCALPHA)
#characters.blit(main_character_image, (0, 0))
#characters.blit(main_character_image, (0, 0))
running = True;
clock = pygame.time.Clock()
delta_time = 0.5
jumping = False
moving_right = False
moving_left = False
running_right = False
running_left = False
state = "Menu"

#sound = pygame.mixer.Sound("sound.wav")
background_image = pygame.image.load(MAP_DATA["image"]).convert()
background_image = pygame.transform.scale( background_image, (WIDTH, HEIGHT))
x = 0
y = 0
while running:

    if state == "Menu":
        main_menu = MainMenu()
        main_menu.__init__(pygame)
        main_menu.create_menu()
    else: 
        game = Game()
        game.__init__(pygame)
        game.create_game()

pygame.quit()




