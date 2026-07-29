import random
from pathlib import Path
import pygame
from levels.generate_characters import FINAL_BOSS, get_main_character
from screens.dialogue_box import DialogueBox

GAME_ROOT = Path(__file__).resolve().parent.parent

class Game:
    ATTACK_DISTANCE = 200
    SPAWN_INTERVAL = 3
    SPAWN_INTERVAL_VARIANCE = 0.25
    SPAWN_OFFSCREEN_MARGIN = 150     
    SCREEN_ENTRY_MARGIN = 150        
    BOSS_SPAWN_OFFSCREEN_MARGIN = 320
    BOSS_SCREEN_ENTRY_MARGIN = 280
    BOSS_INTRO_LOCK = 0.7
    BOSS_ANNOUNCEMENT_DURATION = 2.8

    # Initialize the Game instance with its runtime state.
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
        self.boss_announcement = ""
        self.boss_announcement_timer = 0
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

    # Handle roll spawn delay for the current workflow.
    def _roll_spawn_delay(self):
        return self.SPAWN_INTERVAL + random.uniform(
            -self.SPAWN_INTERVAL_VARIANCE,
            self.SPAWN_INTERVAL_VARIANCE,
        )

    # Return whether final boss matches the current conditions.
    def _is_final_boss(self, character):
        return getattr(character, "is_final_boss", False) or character.type == FINAL_BOSS

    # Handle show boss announcement for the current workflow.
    def _show_boss_announcement(self, enemy):
        self.boss_announcement = (
            enemy.entrance_announcement
            or f"{enemy.display_name.upper()} LLEGA"
        )
        self.boss_announcement_timer = self.BOSS_ANNOUNCEMENT_DURATION

    # Handle trigger boss intro for the current workflow.
    def _trigger_boss_intro(self, enemy):
        if getattr(enemy, "_boss_intro_triggered", False):
            return

        enemy._boss_intro_triggered = True
        enemy.current_line = enemy.intro_line or "He llegado para terminar esto."
        enemy.show_dialogue = True
        enemy.line_timer = 3.4
        enemy.action_lock_timer = max(enemy.action_lock_timer, self.BOSS_INTRO_LOCK)
        enemy.stop()

    # Update spawns for the current frame or state.
    def _update_spawns(self):
        if not self._spawn_queue:
            return

        active_final_boss = next(
            (
                enemy for enemy in self.enemies
                if self._is_final_boss(enemy) and enemy.spawned and not enemy.dead
            ),
            None,
        )
        if active_final_boss is not None:
            return

        self._spawn_timer -= self.delta_time
        if self._spawn_timer <= 0:
            enemy = self._spawn_queue.pop(0)
            self._spawn_enemy(enemy)
            self._spawn_timer = self._roll_spawn_delay()

    # Handle spawn enemy for the current workflow.
    def _spawn_enemy(self, enemy):
        # Aparece justo fuera del borde derecho de la pantalla/background,
        # no en mitad de la pantalla.
        spawn_margin = self.SPAWN_OFFSCREEN_MARGIN
        if self._is_final_boss(enemy):
            spawn_margin = self.BOSS_SPAWN_OFFSCREEN_MARGIN
            enemy.set_speed(max(140, int(enemy.regular_speed * 0.78)))
            self._show_boss_announcement(enemy)
        else:
            enemy.set_speed(enemy.regular_speed)

        enemy.x = self.screen.get_width() + spawn_margin
        enemy.y = self.ground_y
        enemy.spawned = True
        enemy.entered_screen = False
        enemy.facing_right = False
        enemy.set_running(True)
        self.level_metrics["enemies_spawned"] += 1

    # Update entering enemy for the current frame or state.
    def _update_entering_enemy(self, enemy):
        """Enemigo ya soltado pero todavía corriendo hacia dentro de pantalla.
        Mientras tanto no participa en la IA ni en el combate."""
        if self._is_final_boss(enemy):
            entry_x = self.screen.get_width() - self.BOSS_SCREEN_ENTRY_MARGIN
        else:
            entry_x = self.screen.get_width() - self.SCREEN_ENTRY_MARGIN
        enemy.move_left(self.delta_time)

        if enemy.x <= entry_x:
            enemy.x = entry_x
            enemy.entered_screen = True
            enemy.decide_action = True  # que la IA tome el control ya mismo
            enemy.set_speed(enemy.regular_speed)
            if self._is_final_boss(enemy):
                self._trigger_boss_intro(enemy)

    ##################################################
    # SCREEN LIMITS
    ##################################################

    # Handle character width for the current workflow.
    def _character_width(self, character):
        image = character.get_current_image()
        return image.get_width() if image is not None else 100

    # Handle clamp to screen for the current workflow.
    def _clamp_to_screen(self, character):
        min_x = 0
        max_x = self.screen.get_width() - self._character_width(character)
        character.x = max(min_x, min(character.x, max_x))

    ##################################################
    # BACKGROUND
    ##################################################
    # Resolve asset path from the available data.
    def _resolve_asset_path(self, path):
        path = Path(path)
        if path.is_absolute():
            return path
        game_relative = GAME_ROOT / path

        if game_relative.exists():
            return game_relative

        return Path.cwd() / path

    # Prepare background before it is used.
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

    # Handle handle event for the current workflow.
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
    # Resolve collision from the available data.
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
    # Update main character state for the current frame or state.
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

    # Update jump for the current frame or state.
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

    # Predict action from the available inputs.
    def _predict_action(self, character):
        distance = character.distance_to(self.main_character)
        
        # Override emotion based on health - low health = fear
        health_ratio = character.health / character.max_health if character.max_health > 0 else 1.0
        if character.never_flee:
            if health_ratio < 0.45:
                emotion_override = "angry"
            elif health_ratio < 0.75:
                emotion_override = "confident"
            else:
                emotion_override = None
        elif health_ratio < 0.3:  # Below 30% health
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
        if emotion == "afraid" and not character.never_flee:
            # Run away from player
            decision = "MOVE_LEFT" if player_is_right else "MOVE_RIGHT"
        elif self._is_final_boss(character) and distance <= self.ATTACK_DISTANCE * 0.9 and character.attack_timer <= 0:
            decision = "ATTACK"
        elif emotion in ("angry", "confident") and distance > self.ATTACK_DISTANCE * 0.6:
            # Charge toward player
            decision = "MOVE_RIGHT" if player_is_right else "MOVE_LEFT"

        # DEBUG: Log state changes
        if not getattr(character, '_last_logged_emotion', None) or character._last_logged_emotion != emotion:
            print(f"[{character.type}] Health: {character.health:.1f}/{character.max_health} ({health_ratio*100:.0f}%) | Emotion: {emotion} | Action: {decision}")
            character._last_logged_emotion = emotion

        return decision
    # Generate dialogue for the current workflow.
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
            "character_name": getattr(character, "display_name", character.name),
            "enemy_type": character.type,
            "personality": character.personality,
            "dialogue_style": getattr(character, "dialogue_style", character.personality),
            "emotion": character.emotion or "neutral",
            "anger": character.anger,
            "fear": character.fear,
            "confidence": character.confidence,
            "category": character.emotion or category,
            "is_final_boss": self._is_final_boss(character),
        }
        character._dialogue_pending = True
        self.dialogue_generator_async.request(character.id, context)

    # Handle poll dialogue for the current workflow.
    def _poll_dialogue(self, character):
        if self.dialogue_generator_async is None:
            return
        line = self.dialogue_generator_async.poll(character.id)
        if line:
            character.current_line = line
            character.show_dialogue = True
            character.line_timer = 3
            character._dialogue_pending = False
    # Handle execute action for the current workflow.
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
            body = character.get_body_rect()
            player = self.main_character.get_body_rect()
            attack_in_range = abs(body.centerx - player.centerx) < 90
            if not character.attacking:
                if attack_in_range:
                    character.attack()
                else:
                    if body.centerx < player.centerx:
                        character.move_right(self.delta_time)
                    else:
                        character.move_left(self.delta_time)
                    character.last_action = "CHASE_FOR_ATTACK"
                    return
            character.set_running(False)

            character.last_action = action

    # Update enemies for the current frame or state.
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

    # Update enemy fallback for the current frame or state.
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

        if enemy.action_lock_timer > 0:
            enemy.stop()
            self._clamp_to_screen(enemy)
            return

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

    # Handle evaluate action for the current workflow.
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
            if reciever.action_lock_timer > 0:
                reciever.stop()
                if reciever is not self.main_character:
                    self._resolve_collision(reciever, self.main_character)
                    self._clamp_to_screen(reciever)
                reciever.update_attack(self.delta_time)
                reciever.update_animation(self.delta_time)
                reciever.update_status_timers(self.delta_time)
                continue
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
    # Handle try hit for the current workflow.
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
    # Return font for the current flow.
    def _get_font(self, attr, size, bold=True):
        font = getattr(self, attr)
        if font is None:
            font = self.game.font.SysFont("Courier", size, bold=bold)
            setattr(self, attr, font)
        return font

    # Draw character on the current screen or surface.
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

    # Handle health ratio for the current workflow.
    def _health_ratio(self, character):
        if not character.max_health:
            return 0
        return max(0, character.health) / character.max_health

    # Handle health color for the current workflow.
    def _health_color(self, ratio):
        if ratio > 0.5:
            return (0, 200, 0)
        if ratio > 0.25:
            return (230, 200, 0)
        return (200, 0, 0)

    # Draw health bar on the current screen or surface.
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

    # Draw main character health bar on the current screen or surface.
    def _draw_main_character_health_bar(self):
        width, height = 420, 38
        margin = 28
        x = margin
        y = self.screen.get_height() - margin - height

        ratio = self._health_ratio(self.main_character)
        self._draw_health_bar(x, y, width, height, ratio, border=3)

        font = self._get_font("_health_font", 20)
        display_health = int(round(100 * ratio))
        label = f"{max(0, display_health)} / 100"
        text_surface = font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    # Draw enemy health bar on the current screen or surface.
    def _draw_enemy_health_bar(self, enemy):
        if self._is_final_boss(enemy):
            return
        width, height = 80, 10
        x = enemy.x + (self._character_width(enemy) - width) // 2
        img = enemy.get_current_image()
        sprite_top = enemy.y - (img.get_height() if img else 340)
        y = sprite_top - 16
        ratio = self._health_ratio(enemy)
        self._draw_health_bar(x, y, width, height, ratio, border=1)

    # Draw final boss health bar on the current screen or surface.
    def _draw_final_boss_health_bar(self):
        boss = next(
            (
                enemy for enemy in self.enemies
                if self._is_final_boss(enemy) and enemy.spawned
            ),
            None,
        )
        if boss is None:
            return

        width, height = 420, 38
        margin = 28
        x = self.screen.get_width() - margin - width
        y = self.screen.get_height() - margin - height

        ratio = self._health_ratio(boss)
        self._draw_health_bar(x, y, width, height, ratio, border=3)

        title_font = self._get_font("_emotion_font", 20)
        health_font = self._get_font("_health_font", 20)
        name_surface = title_font.render(boss.display_name, True, (255, 226, 170))
        self.screen.blit(name_surface, (x, y - 30))

        label = f"{max(0, int(boss.health))} / {int(boss.max_health)}"
        text_surface = health_font.render(label, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    # Draw emotion on the current screen or surface.
    def _draw_emotion(self, character, anchor_y):
        if not character.show_emotion or not character.emotion:
            return
        font = self._get_font("_emotion_font", 16)
        surface = font.render(character.emotion.capitalize(), True, (255, 230, 0))
        center_x = character.x + self._character_width(character) // 2
        rect = surface.get_rect(midbottom=(center_x, anchor_y))
        self.screen.blit(surface, rect)
    # Draw enemy overlay on the current screen or surface.
    def _draw_enemy_overlay(self, enemy):
        img = enemy.get_current_image()
        sprite_top = enemy.y - (img.get_height() if img else 340)
        # 1) health bar just above sprite top
        self._draw_enemy_health_bar(enemy)
        # 2) emotion label just above health bar
        self._draw_emotion(enemy, sprite_top - 30)
        # 3) dialogue box above emotion
        self.dialogue_box.draw(self.screen, enemy)

    # Draw main character overlay on the current screen or surface.
    def _draw_main_character_overlay(self):
        self._draw_main_character_health_bar()
        img = self.main_character.get_current_image()
        sprite_top = self.main_character.y - (img.get_height() if img else 340)
        self._draw_emotion(self.main_character, sprite_top - 30)
        self.dialogue_box.draw(self.screen, self.main_character)

    # Draw controls overlay on the current screen or surface.
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

    # Draw level overlay on the current screen or surface.
    def _draw_level_overlay(self):
        panel_rect = pygame.Rect(24, 24, 220, 72)
        panel = self.game.Surface(panel_rect.size, self.game.SRCALPHA)
        self.game.draw.rect(panel, (12, 17, 28, 190), panel.get_rect(), border_radius=18)
        self.game.draw.rect(panel, (255, 226, 170, 45), panel.get_rect(), width=2, border_radius=18)
        self.screen.blit(panel, panel_rect.topleft)

        title_font = self._get_font("_emotion_font", 18)
        level_font = self._get_font("_dialogue_font", 30)
        title = title_font.render("Current Level", True, (255, 226, 170))
        level_text = level_font.render(f"Level {self.level}", True, (245, 245, 245))

        self.screen.blit(title, (panel_rect.x + 18, panel_rect.y + 10))
        self.screen.blit(level_text, (panel_rect.x + 18, panel_rect.y + 32))

    # Draw boss announcement on the current screen or surface.
    def _draw_boss_announcement(self):
        if self.boss_announcement_timer <= 0 or not self.boss_announcement:
            return

        width = min(720, self.screen.get_width() - 80)
        panel_rect = pygame.Rect(0, 38, width, 66)
        panel_rect.centerx = self.screen.get_width() // 2
        panel = self.game.Surface(panel_rect.size, self.game.SRCALPHA)
        self.game.draw.rect(panel, (25, 8, 8, 220), panel.get_rect(), border_radius=18)
        self.game.draw.rect(panel, (214, 176, 68, 200), panel.get_rect(), width=3, border_radius=18)
        self.screen.blit(panel, panel_rect.topleft)

        font = self._get_font("_dialogue_font", 28)
        text_surface = font.render(self.boss_announcement, True, (255, 235, 180))
        text_rect = text_surface.get_rect(center=panel_rect.center)
        self.screen.blit(text_surface, text_rect)

    ##################################################
    # GAME LOOP
    ##################################################
    # Create game for the current workflow.
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
        if self.boss_announcement_timer > 0:
            self.boss_announcement_timer = max(0, self.boss_announcement_timer - self.delta_time)
        
        # Update physics and remove dead enemies
        for enemy in self.enemies:
            if enemy.dead:
                enemy.update_physics(self.delta_time, self.ground_y)
        
        # Remove enemies marked for removal
        self.enemies = [e for e in self.enemies if not e.should_remove]
        
        self.level_time += self.delta_time
        self._draw_level_overlay()
        self._draw_boss_announcement()
        self._draw_character(self.main_character)
        self._draw_main_character_overlay()
        self._draw_final_boss_health_bar()
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

    # Return level statistics for the current flow.
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
