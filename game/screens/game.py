import random
from pathlib import Path
import pygame
from levels.generate_characters import get_main_character
from screens.dialogue_box import DialogueBox

GAME_ROOT = Path(__file__).resolve().parent.parent

class Game:
    ATTACK_DISTANCE = 200
    SPAWN_INTERVAL = 3
    SPAWN_INTERVAL_VARIANCE = 0.25
    SPAWN_OFFSCREEN_MARGIN = 150     
    SCREEN_ENTRY_MARGIN = 150        

    def __init__(
            self,
            game,
            running,
            screen,
            enemies,
            background_image,
            delta_time,
            direction,
            decision_manager,
            dialogue_generator_async,
            level=1,
            difficulty_adjuster=None,
    ):  

        self.dialogue_box = DialogueBox()
        self.game = game
        self.running_game = running
        self.screen = screen
        self.decision_manager = decision_manager
        self.dialogue_generator_async = dialogue_generator_async
        self.main_character = get_main_character()
        self.enemies = enemies
        self.level = level
        self.difficulty_adjuster = difficulty_adjuster
        self.level_over = False
        self.background_image = background_image
        self._prepared_background_source = None
        self._prepared_background = None
        self.delta_time = delta_time
        self.direction = direction
        self.jump_velocity = 700
        self.gravity = 1000
        self.ground_y = self.screen.get_height() - 80 # feet land here
        self.auto_mode = False
        #DIALOGUE
        self._prepared_dialogue_box = None
        self._dialogue_font = None
        self._emotion_font = None
        self._health_font = None
        self._controls_font = None
        self.vertical_velocity = 0
        self.return_to_menu_requested = False

        self.level_time = 0.0
        self.level_metrics = {
            "level": self.level,
            "enemies_spawned": 0,
            "enemies_killed": 0,
            "player_attacks": 0,
            "player_hits": 0,
        }

        if self.main_character is not None:
            self.main_character.y = self.ground_y
            self.main_character._death_counted = False
        self._spawn_queue = list(self.enemies)
        self._spawn_timer = 0.35

        for enemy in self.enemies:
            enemy.y = self.ground_y
            enemy.spawned = False
            enemy.entered_screen = False

    ##################################################
    # SPAWN DE ENEMIGOS
    ##################################################

    def _roll_spawn_delay(self):
        return self.SPAWN_INTERVAL + random.uniform(
            -self.SPAWN_INTERVAL_VARIANCE,
            self.SPAWN_INTERVAL_VARIANCE,
        )

    def _update_spawns(self):
        if not self._spawn_queue:
            return

        self._spawn_timer -= self.delta_time
        if self._spawn_timer <= 0:
            enemy = self._spawn_queue.pop(0)
            self._spawn_enemy(enemy)
            self._spawn_timer = self._roll_spawn_delay()

    def _spawn_enemy(self, enemy):
        # Aparece justo fuera del borde derecho de la pantalla/background,
        # no en mitad de la pantalla.
        enemy.x = self.screen.get_width() + self.SPAWN_OFFSCREEN_MARGIN
        enemy.y = self.ground_y
        enemy.spawned = True
        enemy.entered_screen = False
        enemy.facing_right = False
        enemy.set_running(True)
        self.level_metrics["enemies_spawned"] += 1

    def _update_entering_enemy(self, enemy):
        """Enemigo ya soltado pero todavía corriendo hacia dentro de pantalla.
        Mientras tanto no participa en la IA ni en el combate."""
        entry_x = self.screen.get_width() - self.SCREEN_ENTRY_MARGIN
        enemy.move_left(self.delta_time)

        if enemy.x <= entry_x:
            enemy.entered_screen = True
            enemy.decide_action = True  # que la IA tome el control ya mismo

    ##################################################
    # SCREEN LIMITS
    ##################################################

    def _character_width(self, character):
        image = character.get_current_image()
        return image.get_width() if image is not None else 100

    def _clamp_to_screen(self, character):
        min_x = 0
        max_x = self.screen.get_width() - self._character_width(character)
        character.x = max(min_x, min(character.x, max_x))

    ##################################################
    # BACKGROUND
    ##################################################
    def _resolve_asset_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return path
        game_relative = GAME_ROOT / path

        if game_relative.exists():
            return game_relative

        return Path.cwd() / path

    def _prepare_background(self, background):

        if (
                background == self._prepared_background_source
                and self._prepared_background is not None
        ):
            return self._prepared_background

        if isinstance(background, (str, Path)):
            background_path = self._resolve_asset_path(background)

            background = self.game.image.load(
                str(background_path)
            ).convert()

        self._prepared_background_source = background

        self._prepared_background = pygame.transform.scale(
            background,
            self.screen.get_size()
        )

        return self._prepared_background

    ##################################################
    # INPUT
    ##################################################

    def handle_event(self, event):
        if event is None:
            return None

        if event.type == self.game.KEYDOWN:
            if event.key == self.game.K_m:
                self.return_to_menu_requested = True
                return "menu"

            if event.key == self.game.K_SPACE:

                if (
                        not self.main_character.jumping
                        and self.main_character.y >= self.ground_y - 1
                ):

                    self.main_character.set_jumping(True)
                    self.vertical_velocity = -560

            elif event.key == self.game.K_j:
                self.main_character.attack()

        if (
                event.type == self.game.MOUSEBUTTONDOWN
                and event.button == 1
        ):
            self.main_character.attack()

        return None

        
    ##################################################
    # COLLISION
    ##################################################
    def _resolve_collision(self, first, second):
        # Dead enemies don't collide
        if first.dead or second.dead:
            return
        
        rect1 = first.get_body_rect()
        rect2 = second.get_body_rect()
        if not rect1.colliderect(rect2):
            return
        
        # Only push player if other is enemy
        if first is self.main_character:
            # Push player back slightly
            if rect1.centerx < rect2.centerx:
                first.x -= 5
            else:
                first.x += 5
        elif second is self.main_character:
            # Push enemy back
            if rect1.centerx < rect2.centerx:
                second.x += 5
            else:
                second.x -= 5
    ##################################################
    # PLAYER
    ##################################################
    def _update_main_character_state(self, keys):
        if self.auto_mode:
            self.evaluate_action()
        else:
            self._poll_dialogue(self.main_character)
            moving_left = keys[self.game.K_a]
            moving_right = keys[self.game.K_d]

            wants_run = (
                    keys[self.game.K_LSHIFT]
                    or keys[self.game.K_RSHIFT]
            )
            self.main_character.set_running(False)
            for enemy in self.enemies:
                if not enemy.spawned:
                    continue
                if enemy.dead:
                    continue
                # ¿El enemigo golpea al jugador?
                self._try_hit(
                    enemy,
                    self.main_character
                )
                # ¿El jugador golpea al enemigo? (antes esto nunca se
                # comprobaba, por eso los enemigos no perdían vida)
                self._try_hit(
                    self.main_character,
                    enemy
                )
            if moving_right and not moving_left:
                if wants_run:
                    self.main_character.set_speed(self.main_character.sprinting_speed)
                else:
                    self.main_character.set_speed(self.main_character.regular_speed)
                self.main_character.move_right(self.delta_time)
                self.main_character.facing_right = True
                self.main_character.set_running(True)

            elif moving_left and not moving_right:
                if wants_run:
                    self.main_character.set_speed(self.main_character.sprinting_speed)
                else:
                    self.main_character.set_speed(self.main_character.regular_speed)
                self.main_character.move_left(self.delta_time)
                self.main_character.facing_right = False
                self.main_character.set_running(True)
            else:
                self.main_character.stop()

    def _update_jump(self):

        if not self.main_character.jumping:
            return

        self.main_character.y += (
                self.vertical_velocity * self.delta_time
        )

        self.vertical_velocity += (
                self.gravity * self.delta_time
        )

        if self.main_character.y >= self.ground_y:

            self.main_character.y = self.ground_y
            self.main_character.set_jumping(False)
            self.vertical_velocity = 0

    ##################################################
    # ACTIONS
    ##################################################

    def _predict_action(self, character):
        distance = character.distance_to(self.main_character)
        
        # Override emotion based on health - low health = fear
        health_ratio = character.health / character.max_health if character.max_health > 0 else 1.0
        if health_ratio < 0.3:  # Below 30% health
            emotion_override = "afraid"
        elif health_ratio < 0.6:  # Below 60% health
            emotion_override = "angry"
        else:
            emotion_override = None
        
        features = {
            "enemy_type": character.type,
            "enemy_personality": character.personality,
            "enemy_emotion": character.emotion,
            "enemy_health": character.health,
            "enemy_strength": character.strength,
            "enemy_speed": character.speed,
            "enemy_running": character.running,
            "enemy_jumping": character.jumping,
            "enemy_attacking": character.attacking,
            "enemy_dead": character.dead,
            "enemy_facing_right": character.facing_right,
            "enemy_animation_state": character.animation_state,
            "enemy_anger": character.anger,
            "enemy_fear": character.fear,
            "enemy_confidence": character.confidence,
            "enemy_last_action": character.last_action,
            "enemy_times_hit": character.times_hit,
            "enemy_times_attack": character.times_attack,
            "player_health": self.main_character.health,
            "player_strength": self.main_character.strength,
            "player_running": self.main_character.running,
            "player_jumping": self.main_character.jumping,
            "player_attacking": self.main_character.attacking,
            "player_dead": self.main_character.dead,
            "player_facing_right": self.main_character.facing_right,
            "player_animation_state": self.main_character.animation_state,
            "distance": distance,
            "player_is_right": int(self.main_character.x > character.x),
        }

        prediction = self.decision_manager.model.predict(features)
        decision = prediction.decision
        emotion = emotion_override if emotion_override else prediction.emotion

        # Update emotions and apply changes
        character.emotion = emotion
        character.calculate_emotions()

        # Emotion overrides action — afraid = flee, angry = attack or charge
        player_is_right = int(self.main_character.x > character.x)
        if emotion == "afraid":
            # Run away from player
            decision = "MOVE_LEFT" if player_is_right else "MOVE_RIGHT"
        elif emotion == "angry" and distance > self.ATTACK_DISTANCE * 0.6:
            # Charge toward player
            decision = "MOVE_RIGHT" if player_is_right else "MOVE_LEFT"

        # DEBUG: Log state changes
        if not getattr(character, '_last_logged_emotion', None) or character._last_logged_emotion != emotion:
            print(f"[{character.type}] Health: {character.health:.1f}/{character.max_health} ({health_ratio*100:.0f}%) | Emotion: {emotion} | Action: {decision}")
            character._last_logged_emotion = emotion

        return decision
    def _generate_dialogue(self, character, category=None):
        if self.dialogue_generator_async is None:
            return

        # Only request dialogue if none is pending
        if getattr(character, '_dialogue_pending', False):
            return

        # Separate dialogue timer — much less frequent than decision timer
        now = getattr(self, '_dialogue_clock', 0)
        last = getattr(character, '_last_dialogue_time', -999)
        if now - last < 2.5:  # at most every 1.5 seconds per enemy
            return
        character._last_dialogue_time = now

        # Pass current emotion so LLM generates matching dialogue
        context = {
            "enemy_type": character.type,
            "personality": character.personality,
            "emotion": character.emotion or "neutral",
            "anger": character.anger,
            "fear": character.fear,
            "confidence": character.confidence,
            "category": character.emotion or category,
        }
        character._dialogue_pending = True
        self.dialogue_generator_async.request(character.id, context)

    def _poll_dialogue(self, character):
        if self.dialogue_generator_async is None:
            return
        line = self.dialogue_generator_async.poll(character.id)
        if line:
            character.current_line = line
            character.show_dialogue = True
            character.line_timer = 3
            character._dialogue_pending = False
    def _execute_action(self, character, action):

        if action == "MOVE_RIGHT":
            character.move_right(
                self.delta_time
            )
            character.facing_right = True
            character.set_running(True)
            character.last_action = action
        elif action == "MOVE_LEFT":
            character.move_left(
                self.delta_time
            )
            character.facing_right = False
            character.set_running(True)
            character.last_action = action
        elif action == "IDLE" or action is None:
            character.stop()
            character.set_running(False)
            character.last_action = action
        elif action == "ATTACK":
            if character is self.main_character and not character.attacking:
                self.level_metrics["player_attacks"] += 1
            if not character.attacking:
                body = character.get_body_rect()
                player = self.main_character.get_body_rect()
                if abs(body.centerx - player.centerx) < 90:
                    character.attack()
            character.set_running(False)

            character.last_action = action

    def _update_enemies(self):
        if self.decision_manager is None:
            self._update_spawns()
            for enemy in self.enemies:
                if not enemy.spawned:
                    continue
                if not enemy.entered_screen:
                    self._update_entering_enemy(enemy)
                else:
                    self._update_enemy_fallback(enemy)
                enemy.update_attack(self.delta_time)
                enemy.update_animation(self.delta_time)
                enemy.update_status_timers(self.delta_time)
            return

        self.evaluate_action(self.main_character)

    def _update_enemy_fallback(self, enemy):
        distance = enemy.distance_to(self.main_character)
        enemy.facing_right = enemy.x < self.main_character.x

        # Diálogo del enemigo: antes esto nunca se llamaba en el modo sin
        # decision_manager, así que ningún enemigo pedía ni mostraba línea.
        self._poll_dialogue(enemy)
        enemy.decision_timer += self.delta_time
        if enemy.decision_timer >= enemy.decision_interval:
            self._generate_dialogue(enemy)
            enemy.decision_timer = 0

        if distance > self.ATTACK_DISTANCE * 0.7:
            if enemy.facing_right:
                enemy.move_right(self.delta_time)
            else:
                enemy.move_left(self.delta_time)
        else:
            enemy.stop()
            if not enemy.attacking and enemy.attack_timer <= 0:
                enemy.attack()

        self._try_hit(enemy, self.main_character)
        self._try_hit(self.main_character, enemy)
        self._resolve_collision(enemy, self.main_character)
        self._clamp_to_screen(enemy)

    def evaluate_action(self, agresor=None):
     
        self._update_spawns()

        for enemy in self.enemies:
            if not enemy.spawned:
                continue
            if not enemy.entered_screen:
                self._update_entering_enemy(enemy)
                enemy.update_animation(self.delta_time)
                continue
            if agresor == self.main_character:
                 reciever = enemy
            else:
                reciever = self.main_character
                
            self._poll_dialogue(reciever)
            self._try_hit(
                agresor,
                reciever
            )
            reciever.decision_timer += self.delta_time
            if reciever.decision_timer >= enemy.decision_interval:
                reciever.decide_action = True
                reciever.decision_timer = 0
            if reciever.decide_action:
                self._generate_dialogue(reciever)
                reciever.current_action = self._predict_action(reciever)
                reciever.decide_action = False
            self._execute_action(
                reciever,
                reciever.current_action
            )
            # Evita que atraviesen al jugador
            if reciever is not self.main_character:
                self._resolve_collision(reciever, self.main_character)
                self._clamp_to_screen(reciever)

            reciever.update_attack(self.delta_time)
            reciever.update_animation(self.delta_time)
            reciever.update_status_timers(self.delta_time)
    def _try_hit(self, attacker, victim):

        if not attacker.attacking:
            return
        if attacker.damage_done:
            return
        frames = attacker.get_animation_frames()
        if len(frames) == 0:
            return
        middle = len(frames) // 2
        if attacker.animation_frame < middle:
            return
        attack = attacker.get_attack_rect()
        body = victim.get_body_rect()
        if attack.colliderect(body):
            victim.receive_damage(
                attacker.punching_damage
            )
            attacker.damage_done = True
            if attacker is self.main_character:
                self.level_metrics["player_hits"] += 1
            if victim is not self.main_character and victim.dead:
                if not getattr(victim, "_killed_counted", False):
                    self.level_metrics["enemies_killed"] += 1
                    victim._killed_counted = True
    ##################################################
    # DRAW
    ##################################################
    def _get_font(self, attr, size, bold=True):
        font = getattr(self, attr)
        if font is None:
            font = self.game.font.SysFont("Courier", size, bold=bold)
            setattr(self, attr, font)
        return font

    def _draw_character(self, character):

        image = character.get_current_image()

        if image is None:
            return

        # Use locked death direction, never flip a dead character
        if character.dead:
            flip = not getattr(character, '_death_facing_right', character.facing_right)
        else:
            flip = not character.facing_right

        if flip:
            image = self.game.transform.flip(image, True, False)

        # y is always the feet position — draw sprite above it
        draw_y = character.y - image.get_height()

        self.screen.blit(image, (character.x, draw_y))

    def _health_ratio(self, character):
        if not character.max_health:
            return 0
        return max(0, character.health) / character.max_health

    def _health_color(self, ratio):
        if ratio > 0.5:
            return (0, 200, 0)
        if ratio > 0.25:
            return (230, 200, 0)
        return (200, 0, 0)

    def _draw_health_bar(self, x, y, width, height, ratio, border=2):
        # borde
        self.game.draw.rect(
            self.screen, (20, 20, 20),
            (x - border, y - border, width + border * 2, height + border * 2)
        )
        # fondo vacío
        self.game.draw.rect(self.screen, (90, 0, 0), (x, y, width, height))
        # relleno según vida
        fill_width = int(width * ratio)
        if fill_width > 0:
            self.game.draw.rect(
                self.screen, self._health_color(ratio),
                (x, y, fill_width, height)
            )

    def _draw_main_character_health_bar(self):
        width, height = 420, 38
        margin = 28
        x = margin
        y = self.screen.get_height() - margin - height

        ratio = self._health_ratio(self.main_character)
        self._draw_health_bar(x, y, width, height, ratio, border=3)

        font = self._get_font("_health_font", 20)
        label = f"{max(0, int(self.main_character.health))} / {int(self.main_character.max_health)}"
        text_surface = font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def _draw_enemy_health_bar(self, enemy):
        width, height = 80, 10
        x = enemy.x + (self._character_width(enemy) - width) // 2
        img = enemy.get_current_image()
        sprite_top = enemy.y - (img.get_height() if img else 340)
        y = sprite_top - 16
        ratio = self._health_ratio(enemy)
        self._draw_health_bar(x, y, width, height, ratio, border=1)

    def _draw_emotion(self, character, anchor_y):
        if not character.show_emotion or not character.emotion:
            return
        font = self._get_font("_emotion_font", 16)
        surface = font.render(character.emotion.capitalize(), True, (255, 230, 0))
        center_x = character.x + self._character_width(character) // 2
        rect = surface.get_rect(midbottom=(center_x, anchor_y))
        self.screen.blit(surface, rect)
    def _draw_enemy_overlay(self, enemy):
        img = enemy.get_current_image()
        sprite_top = enemy.y - (img.get_height() if img else 340)
        # 1) health bar just above sprite top
        self._draw_enemy_health_bar(enemy)
        # 2) emotion label just above health bar
        self._draw_emotion(enemy, sprite_top - 30)
        # 3) dialogue box above emotion
        self.dialogue_box.draw(self.screen, enemy)

    def _draw_main_character_overlay(self):
        self._draw_main_character_health_bar()
        img = self.main_character.get_current_image()
        sprite_top = self.main_character.y - (img.get_height() if img else 340)
        self._draw_emotion(self.main_character, sprite_top - 30)
        self.dialogue_box.draw(self.screen, self.main_character)

    def _draw_controls_overlay(self):
        font = self._get_font("_controls_font", 18, bold=False)
        panel_rect = pygame.Rect(self.screen.get_width() - 340, 24, 300, 170)
        panel = self.game.Surface(panel_rect.size, self.game.SRCALPHA)
        self.game.draw.rect(panel, (12, 17, 28, 190), panel.get_rect(), border_radius=18)
        self.game.draw.rect(panel, (255, 255, 255, 30), panel.get_rect(), width=2, border_radius=18)
        self.screen.blit(panel, panel_rect.topleft)

        title = self._get_font("_emotion_font", 20).render("Controls", True, (255, 226, 170))
        self.screen.blit(title, (panel_rect.x + 18, panel_rect.y + 14))

        lines = [
            "A / D  Move",
            "Shift  Sprint",
            "Space  Jump",
            "J or Click  Attack",
            "M  Menu",
        ]
        for index, line in enumerate(lines):
            text = font.render(line, True, (236, 239, 245))
            self.screen.blit(text, (panel_rect.x + 18, panel_rect.y + 48 + index * 24))

    ##################################################
    # GAME LOOP
    ##################################################
    def create_game(self, event, delta_time=None):

        if delta_time is not None:
            self.delta_time = delta_time
        background = self._prepare_background(self.background_image)
        self.screen.blit(background, (0, 0))
        keys = self.game.key.get_pressed()

        self._update_main_character_state(keys)
        self._update_jump()
        self.main_character.update_animation(self.delta_time)
        self.main_character.update_attack(self.delta_time)
        self.main_character.update_status_timers(self.delta_time)

        self._clamp_to_screen(self.main_character)
        self._update_enemies()
        self._dialogue_clock = getattr(self, '_dialogue_clock', 0) + self.delta_time
        
        # Update physics and remove dead enemies
        for enemy in self.enemies:
            if enemy.dead:
                enemy.update_physics(self.delta_time, self.ground_y)
        
        # Remove enemies marked for removal
        self.enemies = [e for e in self.enemies if not e.should_remove]
        
        self.level_time += self.delta_time
        self._draw_character(self.main_character)
        self._draw_main_character_overlay()
        self._draw_controls_overlay()
        for enemy in self.enemies:

            if not enemy.spawned:
                continue
            self._draw_character(enemy)
            self._draw_enemy_overlay(enemy)
            enemy.update_attack(self.delta_time)
        self.game.display.flip()

        if all(enemy.dead for enemy in self.enemies):
            self.level_over = True

        if self.main_character.dead:
            self.level_over = True

    def get_level_statistics(self):
        attacks = self.level_metrics["player_attacks"]
        hits = self.level_metrics["player_hits"]
        return {
            "level": self.level,
            "enemies_spawned": self.level_metrics["enemies_spawned"],
            "enemies_killed": self.level_metrics["enemies_killed"],
            "player_damage_received": round(self.main_character.damage_received, 2),
            "player_health_remaining": round(self.main_character.health, 2),
            "player_attacks": attacks,
            "player_hits": hits,
            "player_accuracy": round(hits / attacks if attacks else 0.0, 3),
            "time_seconds": round(self.level_time, 2),
            "times_player_died": int(self.main_character.dead),
            "times_hit": self.main_character.times_hit,
            "level_passed": int(not self.main_character.dead),
        }