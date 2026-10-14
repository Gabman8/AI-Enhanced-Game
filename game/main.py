import pygame
from pathlib import Path
import sys
from importlib import import_module

from levels.generate_level import generate_level
from levels.adjust_dificulty import DifficultyAdjuster
from screens.finish_screen import FinishScreen
from screens.game import Game
from screens.main_menu import MainMenu

GAME_ROOT = Path(__file__).resolve().parent


pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 2048, 1200
SCREEN = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.SCALED | pygame.FULLSCREEN
)
pygame.display.set_caption("Comando")

FPS = 60
DEFAULT_BACKGROUND = "backgrounds/TimesSquare_background.png"
LEVEL_TRANSITION_DELAY = 1


class NoopDialogueGenerator:
    # Queue a new asynchronous request for later processing.
    def request(self, character_id, context):
        return None

    # Poll the latest available result without blocking the caller.
    def poll(self, character_id):
        return None


# Load dialogue generator from the expected source.
def _load_dialogue_generator():
    try:
        from AI.LLM.dialoge_generator import LocalDialogueLLM, AsyncDialogueLLM
        model_path = GAME_ROOT / "AI" / "models" / "qwen2.5-1.5b-instruct-q4_0.gguf"
        if model_path.exists():
            local_llm = LocalDialogueLLM(model_path=model_path)
            return AsyncDialogueLLM(local_llm)
    except Exception as exc:
        print(f"[Dialogue] LLM not available: {exc}")
    return NoopDialogueGenerator()


# Load AI manager from the expected source.
def _load_ai_manager():
    try:
        model_path = GAME_ROOT / "AI" / "models" / "enemies.pkl"
        if model_path.exists():
            manager_type = import_module("AI.ai_manager").AIManager
            return manager_type("enemies.pkl")
    except Exception as exc:
        print(f"[AI] Decision model not available: {exc}")
    return None


_dialogue_generator = _load_dialogue_generator()
_ai_manager = _load_ai_manager()


# Draw loading screen on the current screen or surface.
def draw_loading_screen(message="Loading mission...", level_number=1):
    SCREEN.fill((9, 14, 24))

    title_font = pygame.font.SysFont("Georgia", 76, bold=True)
    body_font = pygame.font.SysFont("Verdana", 26, bold=True)
    level_font = pygame.font.SysFont("Verdana", 30, bold=True)
    hint_font = pygame.font.SysFont("Verdana", 20)

    card_rect = pygame.Rect(0, 0, 760, 260)
    card_rect.center = (WIDTH // 2, HEIGHT // 2)

    card = pygame.Surface(card_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(card, (18, 24, 38, 245), card.get_rect(), border_radius=30)
    pygame.draw.rect(card, (196, 111, 65), card.get_rect(), width=4, border_radius=30)
    SCREEN.blit(card, card_rect.topleft)

    title_surface = title_font.render("Comando", True, (247, 230, 188))
    body_surface = body_font.render(message, True, (241, 241, 241))
    level_surface = level_font.render(f"Level {max(1, int(level_number))}", True, (255, 213, 126))
    hint_surface = hint_font.render("Preparing background, characters, and enemy wave...", True, (205, 214, 224))

    SCREEN.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, card_rect.y + 84)))
    SCREEN.blit(level_surface, level_surface.get_rect(center=(WIDTH // 2, card_rect.y + 144)))
    SCREEN.blit(body_surface, body_surface.get_rect(center=(WIDTH // 2, card_rect.y + 184)))
    SCREEN.blit(hint_surface, hint_surface.get_rect(center=(WIDTH // 2, card_rect.y + 222)))
    pygame.display.flip()


# Build game session for the current workflow.
def build_game_session(message="Loading mission...", level_number=1, previous_stats=None):
    draw_loading_screen(message, level_number=level_number)
    pygame.event.pump()

    level = generate_level(pygame, level=level_number, previous_stats=previous_stats)
    background_image = level["map_data"]["image"] or DEFAULT_BACKGROUND
    session = Game(
        pygame,
        True,
        SCREEN,
        level["enemies"],
        background_image,
        0.016,
        "Static",
        _ai_manager,
        _dialogue_generator,
        level=level_number,
        difficulty_adjuster=difficulty_adjuster,
    )
    return session


running = True
state = "Menu"
paused_from_game = False
clock = pygame.time.Clock()
finish_screen = FinishScreen(pygame, SCREEN)
difficulty_adjuster = DifficultyAdjuster()
current_level = difficulty_adjuster.get_current_level()
game = build_game_session("Loading first mission...", level_number=current_level, previous_stats=difficulty_adjuster.state.get("last_stats"))

pending_level_transition = None
level_transition_timer = 0.0
music_enabled = True

# Music
_music_path = GAME_ROOT / "music" / "epic_musictracks-epic-action-113888.mp3"
if _music_path.exists():
    try:
        pygame.mixer.music.load(str(_music_path))
        pygame.mixer.music.set_volume(0.45)
        pygame.mixer.music.play(-1)
    except Exception as exc:
        print(f"[Music] Could not load music: {exc}")
        music_enabled = False
else:
    music_enabled = False

main_menu = MainMenu(
    pygame,
    running,
    SCREEN,
    "Black",
    30,
    "Verdana",
    game.background_image or DEFAULT_BACKGROUND,
)


# Handle victory subtitle for the current workflow.
def victory_subtitle():
    completed_level = max(1, difficulty_adjuster.get_current_level() - 1)
    return f"Level {completed_level} completed - click to start the next level"


smoke_test = "--smoke-test" in sys.argv[1:]
smoke_test_event_posted = False

while running:
    delta_time = min(clock.tick(FPS) / 1000.0, 0.1)
    pending_action = None
    state_action = None
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
            running = False
            break

        if state == "Menu":
            action = main_menu.create_menu(event, has_active_game=paused_from_game, paused=paused_from_game, music_enabled=music_enabled)
            if action is not None:
                state_action = action
        elif state == "Game":
            if pending_level_transition is None:
                result = game.handle_event(event)
                if result == "menu":
                    pending_action = "menu"
        elif state == "Death":
            if finish_screen.create_finish_screen(
                event,
                title="You Died",
                subtitle="Click to retry level",
                accent=(233, 77, 77),
            ):
                state_action = "restart_after_death"
        elif state == "Victory":
            if finish_screen.create_finish_screen(
                event,
                title="Level Completed",
                subtitle=victory_subtitle(),
                accent=(88, 200, 124),
            ):
                state_action = "restart_after_victory"

    if not running:
        break

    if state == "Menu":
        if not events:
            main_menu.create_menu(None, has_active_game=paused_from_game, paused=paused_from_game, music_enabled=music_enabled)
        action = state_action
        if action == "toggle_music":
            music_enabled = not music_enabled
            if music_enabled:
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.pause()
        elif action == "reset_difficulty":
            difficulty_adjuster.reset_state()
            current_level = 1
            game = build_game_session(
                "Loading first mission...",
                level_number=current_level,
                previous_stats=difficulty_adjuster.state.get("last_stats"),
            )
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
        elif action == "start":
            current_level = difficulty_adjuster.get_current_level()
            game = build_game_session(
                "Starting new mission...",
                level_number=current_level,
                previous_stats=difficulty_adjuster.state.get("last_stats"),
            )
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            paused_from_game = False
            pending_level_transition = None
        elif action == "resume" and paused_from_game:
            state = "Game"
        elif action == "restart":
            current_level = difficulty_adjuster.get_current_level()
            game = build_game_session(
                "Restarting mission...",
                level_number=current_level,
                previous_stats=difficulty_adjuster.state.get("last_stats"),
            )
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            paused_from_game = False
            pending_level_transition = None
        elif action == "quit":
            running = False

    elif state == "Game":
        if pending_level_transition is not None:
            level_transition_timer -= delta_time
            if level_transition_timer <= 0:
                state = pending_level_transition
                pending_level_transition = None
        else:
            game.create_game(None, delta_time)
            if pending_action == "menu" or game.return_to_menu_requested:
                state = "Menu"
                paused_from_game = True
                game.return_to_menu_requested = False
                main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            elif game.level_over:
                last_stats = game.get_level_statistics()
                difficulty_adjuster.record_level_result(last_stats)
                if game.main_character.dead:
                    pending_level_transition = "Death"
                else:
                    current_level = difficulty_adjuster.get_current_level()
                    pending_level_transition = "Victory"
                level_transition_timer = LEVEL_TRANSITION_DELAY
                paused_from_game = False

    elif state == "Death":
        result = finish_screen.create_finish_screen(
            None,
            title="You Died",
            subtitle="Click to retry level",
            accent=(233, 77, 77),
        )
        if state_action == "restart_after_death" or result:
            last_stats = game.get_level_statistics()
            difficulty_adjuster.record_level_result(last_stats)
            game = build_game_session(
                "Rebuilding the street fight...",
                level_number=difficulty_adjuster.get_current_level(),
                previous_stats=difficulty_adjuster.state.get("last_stats"),
            )
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            pending_level_transition = None

    elif state == "Victory":
        result = finish_screen.create_finish_screen(
            None,
            title="Level Completed",
            subtitle=victory_subtitle(),
            accent=(88, 200, 124),
        )
        if state_action == "restart_after_victory" or result:
            game = build_game_session(
                "Loading another enemy wave...",
                level_number=difficulty_adjuster.get_current_level(),
                previous_stats=difficulty_adjuster.state.get("last_stats"),
            )
            main_menu.set_background_image(game.background_image or DEFAULT_BACKGROUND)
            state = "Game"
            pending_level_transition = None

    if smoke_test and not smoke_test_event_posted:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F10))
        smoke_test_event_posted = True

pygame.quit()
