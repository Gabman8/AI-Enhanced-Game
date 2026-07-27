import pygame

from levels.generate_level import generate_level
from screens.death_screen import DeathScreen
from screens.game import Game
from screens.main_menu import MainMenu


pygame.init()
WIDTH, HEIGHT = 2048, 1200
SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.FULLSCREEN
)
pygame.display.set_caption("Comando")

FPS = 144
DEFAULT_BACKGROUND = "backgrounds/TimesSquare_background.png"


class NoopDialogueGenerator:
    def request(self, character_id, context):
        return None

    def poll(self, character_id):
        return None


def draw_loading_screen(message="Loading mission..."):
    SCREEN.fill((9, 14, 24))

    title_font = pygame.font.SysFont("Georgia", 76, bold=True)
    body_font = pygame.font.SysFont("Verdana", 26, bold=True)
    hint_font = pygame.font.SysFont("Verdana", 20)

    card_rect = pygame.Rect(0, 0, 760, 260)
    card_rect.center = (WIDTH // 2, HEIGHT // 2)

    card = pygame.Surface(card_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, (18, 24, 38, 245), card.get_rect(), border_radius=30)
    pygame.draw.rect(card, (196, 111, 65), card.get_rect(), width=4, border_radius=30)
    SCREEN.blit(card, card_rect.topleft)

    title_surface = title_font.render("Comando", True, (247, 230, 188))
    body_surface = body_font.render(message, True, (241, 241, 241))
    hint_surface = hint_font.render("Preparing background, characters, and enemy wave...", True, (205, 214, 224))

    SCREEN.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, card_rect.y + 84)))
    SCREEN.blit(body_surface, body_surface.get_rect(center=(WIDTH // 2, card_rect.y + 154)))
    SCREEN.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, card_rect.y + 208)))
    pygame.display.flip()


def build_game_session(message="Loading mission..."):
    draw_loading_screen(message)
    pygame.event.pump()

    level = generate_level(pygame)
    background_image = level["map_data"]["image"] or DEFAULT_BACKGROUND
    session = Game(
        pygame,
        True,
        SCREEN,
        level["enemies"],
        background_image,
        0.016,
        "Static",
        None,
        NoopDialogueGenerator(),
    )
    return session


running = True
state = "Menu"
paused_from_game = False
clock = pygame.time.Clock()
death_screen = DeathScreen(pygame, SCREEN)
game = build_game_session("Loading first mission...")

main_menu = MainMenu(
    pygame,
    running,
    SCREEN,
    "Black",
    30,
    "Verdana",
    game.background_image or DEFAULT_BACKGROUND,
)


while running:
    delta_time = min(clock.tick(FPS) / 1000.0, 0.1)
    pending_action = None
    state_action = None
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
            break

        if state == "Menu":
            action = main_menu.create_menu(event, has_active_game=paused_from_game, paused=paused_from_game)
            if action is not None:
                state_action = action
        elif state == "Game":
            result = game.handle_event(event)
            if result == "menu":
                pending_action = "menu"
        elif state == "Death":
            if death_screen.create_death_screen(
                event,
                title="You Died",
                subtitle="Click to jump back into a new run",
                accent=(233, 77, 77),
            ):
                state_action = "restart_after_death"
        elif state == "Victory":
            if death_screen.create_death_screen(
                event,
                title="Level Cleared",
                subtitle="Click to start the next run",
                accent=(88, 200, 124),
            ):
                state_action = "restart_after_victory"

    if not running:
        break

    if state == "Menu":
        if not events:
            main_menu.create_menu(None, has_active_game=paused_from_game, paused=paused_from_game)
        action = state_action
        if action == "start":
            game = build_game_session("Starting new mission...")
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            paused_from_game = False
        elif action == "resume" and paused_from_game:
            state = "Game"
        elif action == "restart":
            game = build_game_session("Restarting mission...")
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            paused_from_game = False
        elif action == "quit":
            running = False

    elif state == "Game":
        game.create_game(None, delta_time)
        if pending_action == "menu" or game.return_to_menu_requested:
            state = "Menu"
            paused_from_game = True
            game.return_to_menu_requested = False
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
        elif game.level_over:
            if game.main_character.dead:
                state = "Death"
            else:
                state = "Victory"
            paused_from_game = False

    elif state == "Death":
        result = death_screen.create_death_screen(
            None,
            title="You Died",
            subtitle="Click to jump back into a new run",
            accent=(233, 77, 77),
        )
        if state_action == "restart_after_death" or result:
            game = build_game_session("Rebuilding the street fight...")
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"

    elif state == "Victory":
        result = death_screen.create_death_screen(
            None,
            title="Level Cleared",
            subtitle="Click to start the next run",
            accent=(88, 200, 124),
        )
        if state_action == "restart_after_victory" or result:
            game = build_game_session("Loading another enemy wave...")
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"

pygame.quit()