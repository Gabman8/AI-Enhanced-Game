import pygame
from levels.generate_level import generate_level
from screens.main_menu import MainMenu
from screens.game import Game
from screens.death_screen import DeathScreen
from AI.ai_manager import AIManager
from AI.LLM.dialoge_generator import AsyncDialogueLLM,LocalDialogueLLM,DialogueContext
pygame.init()
WIDTH, HEIGHT = 2048, 1200
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Comando")

FPS = 144
DEFAULT_BACKGROUND = "backgrounds/TimesSquare_background.png"
LEVEL = generate_level(pygame)

def new_game():
    level = generate_level(pygame)
    background_image = level["map_data"]["image"] or DEFAULT_BACKGROUND
    game = Game(
        pygame,
        True,
        SCREEN,
        level["enemies"],
        background_image,
        0.5,
        direction,
        decision_manager,
        dialogue_generator_async
    )
    return game
running = True
state = "Menu"
clock = pygame.time.Clock()
background_image = LEVEL["map_data"]["image"] or DEFAULT_BACKGROUND
death_screen = DeathScreen(pygame, SCREEN)
decision_manager = AIManager("enemies.pkl")
dialogue_generator= LocalDialogueLLM(
    model_path=r"C:\Users\Gabriel\Documents\Coding\AI-World-Game\game\AI\models\qwen2.5-1.5b-instruct-q4_k_m.gguf"
)
dialogue_generator_async = AsyncDialogueLLM(dialogue_generator)
direction = "Static"

main_menu = MainMenu(
    pygame,
    running,
    SCREEN,
    "Red",
    30,
    "Courier",
    background_image
)

game = new_game()

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
        if game.level_over:
            if game.main_character.dead:
                state = "Death"
            else:
                # ganaste el nivel -> vuelves al menú (o generas otro nivel)
                state = "Menu"
    elif state == "Death":
        if death_screen.create_death_screen(event):
            game = new_game()   # reinicia todo: enemigos, nivel, personaje...
            state = "Menu"
pygame.quit()





