"""
Main Game Logic
Castle Strategy Game
"""

import asyncio
import pygame
import random
from config import *
from castle import Castle
from units import Knight, Archer, Spearman, Mage, Cannon, Hero
from network import NetworkManager


class Game:
    """Main game class"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Castle Strategy - Inspired by Anakin's Castle Duels")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True

        # Game state
        self.state = 'menu'  # menu, multiplayer_menu, searching, playing, game_over
        self.game_mode = 'singleplayer'  # 'singleplayer' or 'multiplayer'
        self.winner = None

        # Multiplayer
        self.network = NetworkManager()
        self.server_url = 'http://localhost:5000'  # Default, can be changed

        # Initialize game objects
        self.reset_game()

    def reset_game(self):
        """Reset game to initial state"""
        # Castles
        self.player_castle = Castle(PLAYER_CASTLE_X, CASTLE_Y, 'player')
        self.enemy_castle = Castle(ENEMY_CASTLE_X, CASTLE_Y, 'enemy')

        # Units
        self.player_units = []
        self.enemy_units = []

        # AI timer
        self.ai_timer = 0
        self.ai_strategy = 'balanced'

        # Spell effects
        self.active_effects = []

        # Game time
        self.game_time = 0

    async def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            self.handle_events()

            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'multiplayer_menu':
                self.draw_multiplayer_menu()
            elif self.state == 'searching':
                self.draw_searching()
                self.check_match_found()
            elif self.state == 'playing':
                self.update(dt)
                self.draw()
            elif self.state == 'game_over':
                self.draw_game_over()

            pygame.display.flip()

            # Yield control back to browser (required for pygbag)
            await asyncio.sleep(0)

        # Clean up
        if self.network.connected:
            self.network.disconnect()
        pygame.quit()

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_1:
                        # Singleplayer
                        self.game_mode = 'singleplayer'
                        self.state = 'playing'
                        self.reset_game()
                    elif event.key == pygame.K_2:
                        # Multiplayer
                        self.state = 'multiplayer_menu'
                    elif event.key == pygame.K_SPACE:
                        # Legacy - default to singleplayer
                        self.game_mode = 'singleplayer'
                        self.state = 'playing'
                        self.reset_game()

                elif self.state == 'multiplayer_menu':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        # Start matchmaking
                        if not self.network.connected:
                            self.network.connect(self.server_url)
                        if self.network.connected:
                            self.network.find_match()
                            self.state = 'searching'
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'

                elif self.state == 'searching':
                    if event.key == pygame.K_ESCAPE:
                        self.network.cancel_search()
                        self.state = 'multiplayer_menu'

                elif self.state == 'playing':
                    self.handle_game_input(event.key)

                elif self.state == 'game_over':
                    if event.key == pygame.K_SPACE:
                        self.state = 'menu'

            if event.type == pygame.MOUSEBUTTONDOWN and self.state == 'playing':
                self.handle_mouse_click(event.pos)

    def handle_game_input(self, key):
        """Handle keyboard input during gameplay"""
        # Unit production
        if key == pygame.K_1:
            self.produce_player_unit('knight')
        elif key == pygame.K_2:
            self.produce_player_unit('archer')
        elif key == pygame.K_3:
            self.produce_player_unit('spearman')
        elif key == pygame.K_4:
            self.produce_player_unit('mage')
        elif key == pygame.K_5:
            self.produce_player_unit('cannon')
        elif key == pygame.K_6:
            self.produce_player_unit('hero')

        # Build mine
        elif key == pygame.K_m:
            if self.player_castle.build_mine():
                # Send to opponent in multiplayer
                if self.game_mode == 'multiplayer' and self.network.in_game:
                    self.network.send_mine_built()

        # Spells
        elif key == pygame.K_f:
            self.cast_player_spell('fireball')
        elif key == pygame.K_h:
            self.cast_player_spell('heal')
        elif key == pygame.K_g:
            self.cast_player_spell('gold_boost')
        elif key == pygame.K_z:
            self.cast_player_spell('freeze')

    def handle_mouse_click(self, pos):
        """Handle mouse clicks on UI buttons"""
        # Check if clicked on unit buttons
        button_y = 150
        button_height = 40
        button_width = 150

        unit_types = ['knight', 'archer', 'spearman', 'mage', 'cannon', 'hero']

        for i, unit_type in enumerate(unit_types):
            button_rect = pygame.Rect(10, button_y + i * (button_height + 10),
                                     button_width, button_height)
            if button_rect.collidepoint(pos):
                self.produce_player_unit(unit_type)
                return

        # Check mine button
        mine_button = pygame.Rect(10, button_y + len(unit_types) * (button_height + 10),
                                 button_width, button_height)
        if mine_button.collidepoint(pos):
            self.player_castle.build_mine()
            return

    def produce_player_unit(self, unit_type):
        """Produce a unit for the player"""
        unit = self.player_castle.produce_unit(unit_type)
        if unit:
            self.player_units.append(unit)
            # Send to opponent in multiplayer
            if self.game_mode == 'multiplayer' and self.network.in_game:
                self.network.send_unit_spawn(unit_type)

    def produce_enemy_unit(self, unit_type):
        """Produce a unit for the enemy"""
        unit = self.enemy_castle.produce_unit(unit_type)
        if unit:
            self.enemy_units.append(unit)

    def cast_player_spell(self, spell_name):
        """Cast a spell for the player"""
        if self.player_castle.cast_spell(spell_name):
            self.apply_spell_effect(spell_name, 'player')
            # Send to opponent in multiplayer
            if self.game_mode == 'multiplayer' and self.network.in_game:
                self.network.send_spell_cast(spell_name)

    def cast_enemy_spell(self, spell_name):
        """Cast a spell for the enemy"""
        if self.enemy_castle.cast_spell(spell_name):
            self.apply_spell_effect(spell_name, 'enemy')

    def apply_spell_effect(self, spell_name, caster):
        """Apply spell effects"""
        spell = SPELLS[spell_name]

        if spell_name == 'fireball':
            # Damage enemy units
            targets = self.enemy_units if caster == 'player' else self.player_units
            for unit in targets[:3]:  # Hit up to 3 units
                if unit.alive:
                    unit.take_damage(spell['damage'])

        elif spell_name == 'heal':
            # Heal castle
            castle = self.player_castle if caster == 'player' else self.enemy_castle
            castle.heal(spell['amount'])

        elif spell_name == 'gold_boost':
            # Add gold
            castle = self.player_castle if caster == 'player' else self.enemy_castle
            castle.gold += spell['amount']

        elif spell_name == 'freeze':
            # Freeze enemy units
            targets = self.enemy_units if caster == 'player' else self.player_units
            for unit in targets:
                if unit.alive:
                    unit.freeze(spell['duration'])

    def update(self, dt):
        """Update game state"""
        self.game_time += dt

        # Update castles
        self.player_castle.update(dt)
        self.enemy_castle.update(dt)

        # Update player units
        for unit in self.player_units:
            unit.update(dt, self.enemy_units, self.enemy_castle)

        # Update enemy units
        for unit in self.enemy_units:
            unit.update(dt, self.player_units, self.player_castle)

        # Remove dead units
        self.player_units = [u for u in self.player_units if u.alive]
        self.enemy_units = [u for u in self.enemy_units if u.alive]

        # Multiplayer: process opponent actions
        if self.game_mode == 'multiplayer' and self.network.in_game:
            self.process_opponent_actions()
        else:
            # AI behavior (only in singleplayer)
            self.update_ai(dt)

        # Check win/lose conditions
        if self.player_castle.is_destroyed():
            self.state = 'game_over'
            self.winner = 'enemy'
        elif self.enemy_castle.is_destroyed():
            self.state = 'game_over'
            self.winner = 'player'

    def update_ai(self, dt):
        """Simple AI logic"""
        self.ai_timer += dt

        if self.ai_timer < AI_REACTION_TIME:
            return

        self.ai_timer = 0

        # Change strategy occasionally
        if random.random() < 0.1:
            self.ai_strategy = random.choice(['aggressive', 'defensive', 'balanced'])

        gold = self.enemy_castle.gold

        # Build mines periodically
        if gold > MINE_COST * 2 and random.random() < 0.3:
            self.enemy_castle.build_mine()

        # Cast spells
        if gold > 1000:
            available_spells = []
            for spell_name, spell_data in SPELLS.items():
                if (self.enemy_castle.spell_cooldowns[spell_name] <= 0 and
                    self.enemy_castle.can_afford(spell_data['cost'])):
                    available_spells.append(spell_name)

            if available_spells and random.random() < 0.3:
                spell = random.choice(available_spells)
                self.cast_enemy_spell(spell)

        # Produce units based on strategy
        if self.ai_strategy == 'aggressive':
            priorities = ['knight', 'hero', 'spearman', 'cannon', 'archer', 'mage']
        elif self.ai_strategy == 'defensive':
            priorities = ['archer', 'mage', 'cannon', 'knight', 'spearman', 'hero']
        else:  # balanced
            priorities = ['knight', 'archer', 'spearman', 'mage', 'cannon', 'hero']

        # Try to produce a unit
        for unit_type in priorities:
            cost = self.enemy_castle.get_unit_cost(unit_type)
            if gold > cost + AI_GOLD_SAVE_THRESHOLD:
                self.produce_enemy_unit(unit_type)
                break

    def draw(self):
        """Draw game"""
        # Background - sky
        self.screen.fill(LIGHT_BLUE)

        # Draw ground
        ground_y = CASTLE_Y
        pygame.draw.rect(self.screen, DARK_GREEN,
                        (0, ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - ground_y))

        # Draw clouds
        self.draw_clouds()

        # Draw castles
        self.player_castle.draw(self.screen)
        self.enemy_castle.draw(self.screen)

        # Draw units
        for unit in self.player_units:
            unit.draw(self.screen)
        for unit in self.enemy_units:
            unit.draw(self.screen)

        # Draw UI
        self.draw_ui()

    def draw_clouds(self):
        """Draw decorative clouds"""
        clouds = [
            (200, 150, 60),
            (500, 100, 50),
            (800, 120, 55),
            (1100, 90, 65),
        ]
        for cx, cy, size in clouds:
            pygame.draw.circle(self.screen, WHITE, (cx, cy), size, 0)
            pygame.draw.circle(self.screen, WHITE, (cx + 30, cy - 10), size - 10, 0)
            pygame.draw.circle(self.screen, WHITE, (cx + 50, cy), size - 5, 0)

    def draw_ui(self):
        """Draw user interface"""
        # Player info panel
        panel_rect = pygame.Rect(5, 5, 360, 130)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 2)

        # Stats
        y_offset = 15
        texts = [
            f"Castle HP: {int(self.player_castle.hp)}/{self.player_castle.max_hp}",
            f"Gold: {int(self.player_castle.gold)}",
            f"Mines: {self.player_castle.mines}",
            f"Units: {len(self.player_units)}"
        ]

        for text in texts:
            surf = self.small_font.render(text, True, WHITE)
            self.screen.blit(surf, (15, y_offset))
            y_offset += 25

        # Enemy info panel (top right)
        enemy_panel = pygame.Rect(SCREEN_WIDTH - 365, 5, 360, 130)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), enemy_panel)
        pygame.draw.rect(self.screen, RED, enemy_panel, 2)

        y_offset = 15
        enemy_texts = [
            f"Enemy HP: {int(self.enemy_castle.hp)}/{self.enemy_castle.max_hp}",
            f"Enemy Gold: {int(self.enemy_castle.gold)}",
            f"Enemy Mines: {self.enemy_castle.mines}",
            f"Enemy Units: {len(self.enemy_units)}"
        ]

        for text in enemy_texts:
            surf = self.small_font.render(text, True, WHITE)
            self.screen.blit(surf, (SCREEN_WIDTH - 355, y_offset))
            y_offset += 25

        # Unit production buttons
        self.draw_unit_buttons()

        # Spell buttons
        self.draw_spell_buttons()

        # Instructions
        inst_y = SCREEN_HEIGHT - 80
        instructions = [
            "Controls: 1-6: Units | M: Mine | F: Fireball | H: Heal | G: Gold | Z: Freeze",
            "Click buttons or use keyboard shortcuts"
        ]
        for i, text in enumerate(instructions):
            surf = self.small_font.render(text, True, WHITE)
            self.screen.blit(surf, (10, inst_y + i * 25))

    def draw_unit_buttons(self):
        """Draw unit production buttons"""
        button_x = 10
        button_y = 150
        button_width = 150
        button_height = 40

        unit_types = [
            ('1: Knight', 'knight'),
            ('2: Archer', 'archer'),
            ('3: Spearman', 'spearman'),
            ('4: Mage', 'mage'),
            ('5: Cannon', 'cannon'),
            ('6: Hero', 'hero')
        ]

        for i, (label, unit_type) in enumerate(unit_types):
            y = button_y + i * (button_height + 10)
            cost = self.player_castle.get_unit_cost(unit_type)
            can_afford = self.player_castle.can_afford(cost)

            # Button background
            color = GREEN if can_afford else GRAY
            button_rect = pygame.Rect(button_x, y, button_width, button_height)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)

            # Button text
            text = f"{label}: {cost}g"
            surf = self.small_font.render(text, True, BLACK if can_afford else DARK_GRAY)
            text_rect = surf.get_rect(center=button_rect.center)
            self.screen.blit(surf, text_rect)

        # Mine button
        y = button_y + len(unit_types) * (button_height + 10)
        can_afford = self.player_castle.can_afford(MINE_COST)
        color = YELLOW if can_afford else GRAY
        button_rect = pygame.Rect(button_x, y, button_width, button_height)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)

        text = f"M: Mine: {MINE_COST}g"
        surf = self.small_font.render(text, True, BLACK if can_afford else DARK_GRAY)
        text_rect = surf.get_rect(center=button_rect.center)
        self.screen.blit(surf, text_rect)

    def draw_spell_buttons(self):
        """Draw spell buttons"""
        button_x = SCREEN_WIDTH - 170
        button_y = 150
        button_width = 160
        button_height = 40

        spells = [
            ('F: Fireball', 'fireball'),
            ('H: Heal', 'heal'),
            ('G: Gold', 'gold_boost'),
            ('Z: Freeze', 'freeze')
        ]

        for i, (label, spell_name) in enumerate(spells):
            y = button_y + i * (button_height + 10)
            spell = SPELLS[spell_name]
            cost = spell['cost']
            cooldown = self.player_castle.spell_cooldowns[spell_name]
            can_cast = cooldown <= 0 and self.player_castle.can_afford(cost)

            # Button background
            if cooldown > 0:
                color = DARK_GRAY
            elif can_cast:
                color = (100, 100, 255)
            else:
                color = GRAY

            button_rect = pygame.Rect(button_x, y, button_width, button_height)
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, BLACK, button_rect, 2)

            # Button text
            if cooldown > 0:
                text = f"{label}: {int(cooldown)}s"
            else:
                text = f"{label}: {cost}g"

            surf = self.small_font.render(text, True, WHITE if can_cast else BLACK)
            text_rect = surf.get_rect(center=button_rect.center)
            self.screen.blit(surf, text_rect)

    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(LIGHT_BLUE)

        # Title
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("CASTLE STRATEGY", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font.render("Inspired by Anakin's Castle Duels", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 280))
        self.screen.blit(subtitle, subtitle_rect)

        # Mode selection
        mode_text = [
            "Select Game Mode:",
            "",
            "Press 1 - Singleplayer vs AI",
            "Press 2 - Multiplayer 1vs1 Online",
            "",
            "Or press SPACE for Singleplayer"
        ]

        y = 380
        for line in mode_text:
            text = self.small_font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 35

    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill((0, 0, 0))

        # Result text
        title_font = pygame.font.Font(None, 72)
        if self.winner == 'player':
            result = title_font.render("VICTORY!", True, GREEN)
        else:
            result = title_font.render("DEFEAT!", True, RED)

        result_rect = result.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(result, result_rect)

        # Continue text
        continue_text = self.font.render("Press SPACE to return to menu", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)

    def draw_multiplayer_menu(self):
        """Draw multiplayer menu"""
        self.screen.fill(LIGHT_BLUE)

        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("MULTIPLAYER 1vs1", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        # Info
        info_text = [
            "Fight against a real player online!",
            "",
            f"Server: {self.server_url}",
            "",
            "Press SPACE to find a match",
            "Press ESC to go back"
        ]

        y = 350
        for line in info_text:
            text = self.small_font.render(line, True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 40

    def draw_searching(self):
        """Draw searching for match screen"""
        self.screen.fill(LIGHT_BLUE)

        # Title
        title_font = pygame.font.Font(None, 64)
        title = title_font.render("SEARCHING FOR OPPONENT...", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title, title_rect)

        # Animated dots
        dots = '.' * (int(self.game_time * 2) % 4)
        waiting = self.font.render(f"Please wait{dots}", True, DARK_GRAY)
        waiting_rect = waiting.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(waiting, waiting_rect)

        # Cancel instruction
        cancel = self.small_font.render("Press ESC to cancel", True, DARK_GRAY)
        cancel_rect = cancel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        self.screen.blit(cancel, cancel_rect)

    def check_match_found(self):
        """Check if match was found and start game"""
        if self.network.in_game and self.state == 'searching':
            # Match found! Start game
            self.game_mode = 'multiplayer'
            self.reset_game()
            self.network.ready()
            self.state = 'playing'
            print(f'Match started! You are {self.network.role}')

    def process_opponent_actions(self):
        """Process opponent actions in multiplayer"""
        actions = self.network.get_opponent_actions()

        for action in actions:
            action_type = action.get('type')

            if action_type == 'unit_spawn':
                unit_type = action.get('unit_type')
                self.produce_enemy_unit(unit_type)

            elif action_type == 'spell_cast':
                spell_name = action.get('spell_name')
                self.cast_enemy_spell(spell_name)

            elif action_type == 'mine_built':
                # Sync opponent's mine count
                self.enemy_castle.mines = action.get('mines', 0)
