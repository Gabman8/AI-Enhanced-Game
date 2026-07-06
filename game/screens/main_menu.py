class MainMenu:
    def __init__(self, screen):
        self.screen=screen
    def create_menu(self,pygame):
        self.screen.fill("blue")
        pygame.get_font(100).render("MAIN MENU", True, "#b68f40") 
        self.screen.blit(color(red), (0, 0))