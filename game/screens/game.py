class Game:
    def __init__(self, game):
        self.game = game
    def create_game(self):
        pygame = self.game
        screen = self.game.display
        clock = pygame.time.clock
        main_character = self.characters[main_character]
        screen(background_image, (0, 0))
        main_character_image.set_alpha(255)
        screen.blit(main_character_image, (x, y))
        hitbox = pygame.Rect(x, y, main_character_image.get_width(), main_character_image.get_height())
        target = pygame.Rect(500, 30, 64, 64)
        collision = hitbox.colliderect(target)
        #pygame.draw.rect(screen, (255, 0, 0), target)

        if moving_right:
            x += 200 *delta_time
        if moving_left:
            x -= 200 *delta_time
        if running_right:
            x += 400 * delta_time
        if running_left:
            x -= 400 * delta_time
        if jumping:
            main_character_image.set_alpha(128)
            y -= 500 * delta_time
            jumping = False    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ''' SAVE FOR MENU
            if event.type == pygame.VIDEORESIZE:
                resolution = screen.get_size()
                background_image = pygame.transform.scale(background_image, resolution)'''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    moving_right = True
                if event.key == pygame.K_a:
                    moving_left = True
                if event.key == pygame.K_SPACE:
                    jumping = True
                if event.key == pygame.K_a and event.key == pygame.K_LSHIFT:
                    moving_left = False
                    moving_right = False
                    running_right = True
                if event.key == pygame.K_d and event.key == pygame.K_LSHIFT:
                    moving_left = False
                    moving_right = False
                    running_left = True
                '''if event.key == pygame.K_f:
                    sound.play()'''
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    moving_right = False
                    main_character_image.set_alpha(255)
                if event.key == pygame.K_a:
                    moving_left = False
                    main_character_image.set_alpha(255)
                if  event.key == pygame.K_LSHIFT:
                    running_right = False
                    running_left = False
                
                '''if event.key == pygame.K_f:
                    sound.stop()'''
        pygame.display.flip() 
        clock.tick(60) 

        delta_time = pygame.time.Clock().tick(60) / 1000.0
        delta_time = min(delta_time, 0.1)


    