import pygame
from characters.character import Character
from levels.generate_map import generate_map

pygame.init()

screen = pygame.display.set_mode((1024, 768))
map_data = generate_map("forest", (100, 100), ["trees", "rocks"], ["goblin", "troll"])
main_character = Character("John", ["strength", "speed"], "brave", "hero");

main_character_image = pygame.image.load("main_character.png").convert_alpha()
main_character_image = pygame.transform.scale(main_character_image, 
                                              (main_character_image.get_width() * 2, 
                                               main_character_image.get_height() * 2))

main_character_image.set_colorkey((255, 255, 255))
#for multiple character this code will be usefull
#characters = pygame.Surface((64, 64), pygame.SRCALPHA)
#characters.blit(main_character_image, (0, 0))
#characters.blit(main_character_image, (0, 0))
running = True;
clock = pygame.time.Clock()
delta_time = 0.1
moving_right = False
moving_left = False
sound = pygame.mixer.Sound("sound.wav")
x = 0
while running:
    screen.fill((200, 200, 100))
    main_character_image.set_alpha(255)
    screen.blit(main_character_image, (x, 100))
    hitbox = pygame.Rect(x, 30, main_character_image.get_width(), main_character_image.get_height())
    target = pygame.Rect(500, 30, 64, 64)
    collision = hitbox.colliderect(target)
    pygame.draw.rect(screen, (255, 0, 0), target)

    if moving_right:
        x += 50 *delta_time
    if moving_left:
        x -= 50 *delta_time
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_f:
                sound.play()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving_right = False
                main_character_image.set_alpha(255)
            if event.key == pygame.K_a:
                moving_left = False
                main_character_image.set_alpha(255)
            if event.key == pygame.K_f:
                sound.stop()
    pygame.display.flip() 
    clock.tick(60) 

    delta_time = pygame.time.Clock().tick(60) / 1000.0
    delta_time = min(delta_time, 0.1)

pygame.quit()
