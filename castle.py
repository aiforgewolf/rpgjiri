"""
Castle Class
Represents player and enemy castles
"""

import pygame
from config import *
from units import Knight, Archer, Spearman, Mage, Cannon, Hero


class Castle:
    """Castle with health, resources, and unit production"""

    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team  # 'player' or 'enemy'

        # Stats
        self.max_hp = CASTLE_STARTING_HP
        self.hp = self.max_hp
        self.gold = STARTING_GOLD
        self.mines = 0

        # Unit counts for cost calculation
        self.unit_counts = {
            'knight': 0,
            'archer': 0,
            'spearman': 0,
            'mage': 0,
            'cannon': 0,
            'hero': 0
        }

        # Spell cooldowns
        self.spell_cooldowns = {spell: 0 for spell in SPELLS}

        # Visual
        self.width = CASTLE_WIDTH
        self.height = CASTLE_HEIGHT
        self.color = BLUE if team == 'player' else RED

    def update(self, dt):
        """Update castle state"""
        # Generate gold
        gold_per_tick = (GOLD_PER_SECOND + self.mines * MINE_GOLD_BONUS) * dt
        self.gold += gold_per_tick

        # Update spell cooldowns
        for spell in self.spell_cooldowns:
            if self.spell_cooldowns[spell] > 0:
                self.spell_cooldowns[spell] -= dt

    def can_afford(self, cost):
        """Check if castle can afford something"""
        return self.gold >= cost

    def spend_gold(self, amount):
        """Spend gold"""
        if self.can_afford(amount):
            self.gold -= amount
            return True
        return False

    def get_unit_cost(self, unit_type):
        """Calculate cost of unit based on number already produced"""
        base_cost = UNIT_COSTS[unit_type]
        count = self.unit_counts[unit_type]
        return int(base_cost * (COST_MULTIPLIER ** count))

    def produce_unit(self, unit_type):
        """Produce a unit if affordable"""
        cost = self.get_unit_cost(unit_type)

        if self.spend_gold(cost):
            self.unit_counts[unit_type] += 1

            # Create unit at castle entrance
            spawn_x = self.x + (50 if self.team == 'player' else -50)
            spawn_y = self.y

            # Create appropriate unit type
            unit_classes = {
                'knight': Knight,
                'archer': Archer,
                'spearman': Spearman,
                'mage': Mage,
                'cannon': Cannon,
                'hero': Hero
            }

            unit_class = unit_classes.get(unit_type)
            if unit_class:
                return unit_class(spawn_x, spawn_y, self.team)

        return None

    def build_mine(self):
        """Build a mine to increase gold generation"""
        if self.spend_gold(MINE_COST):
            self.mines += 1
            return True
        return False

    def cast_spell(self, spell_name):
        """Cast a spell if off cooldown and affordable"""
        if spell_name not in SPELLS:
            return False

        spell = SPELLS[spell_name]

        # Check cooldown
        if self.spell_cooldowns[spell_name] > 0:
            return False

        # Check cost
        if not self.spend_gold(spell['cost']):
            return False

        # Set cooldown
        self.spell_cooldowns[spell_name] = spell['cooldown']
        return True

    def take_damage(self, amount):
        """Take damage"""
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        """Heal castle"""
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_destroyed(self):
        """Check if castle is destroyed"""
        return self.hp <= 0

    def draw(self, screen):
        """Draw castle"""
        # Draw castle body
        castle_rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, self.color, castle_rect)
        pygame.draw.rect(screen, BLACK, castle_rect, 3)

        # Draw castle towers
        tower_width = 40
        tower_height = 80

        # Left tower
        left_tower = pygame.Rect(
            self.x - self.width // 2 - 10,
            self.y - self.height - 30,
            tower_width,
            tower_height
        )
        pygame.draw.rect(screen, self.color, left_tower)
        pygame.draw.rect(screen, BLACK, left_tower, 3)

        # Right tower
        right_tower = pygame.Rect(
            self.x + self.width // 2 - 30,
            self.y - self.height - 30,
            tower_width,
            tower_height
        )
        pygame.draw.rect(screen, self.color, right_tower)
        pygame.draw.rect(screen, BLACK, right_tower, 3)

        # Draw battlements
        battlement_width = 15
        battlement_height = 20
        for i in range(5):
            x = self.x - self.width // 2 + i * 30
            y = self.y - self.height
            pygame.draw.rect(screen, self.color,
                           (x, y - battlement_height, battlement_width, battlement_height))
            pygame.draw.rect(screen, BLACK,
                           (x, y - battlement_height, battlement_width, battlement_height), 2)

        # Draw HP bar
        bar_width = self.width
        bar_height = 15
        hp_ratio = self.hp / self.max_hp

        # Background (red)
        pygame.draw.rect(screen, RED,
                        (self.x - bar_width // 2, self.y - self.height - 60,
                         bar_width, bar_height))
        # Health (green)
        pygame.draw.rect(screen, GREEN,
                        (self.x - bar_width // 2, self.y - self.height - 60,
                         bar_width * hp_ratio, bar_height))
        # Border
        pygame.draw.rect(screen, BLACK,
                        (self.x - bar_width // 2, self.y - self.height - 60,
                         bar_width, bar_height), 2)

        # Draw HP text
        font = pygame.font.Font(None, 20)
        hp_text = font.render(f"{int(self.hp)}/{self.max_hp}", True, WHITE)
        text_rect = hp_text.get_rect(center=(self.x, self.y - self.height - 52))
        screen.blit(hp_text, text_rect)
