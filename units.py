"""
Unit Classes
Different unit types for the castle strategy game
"""

import pygame
import math
from config import *


class Unit:
    """Base class for all units"""

    def __init__(self, x, y, team, unit_type):
        self.x = x
        self.y = y
        self.team = team  # 'player' or 'enemy'
        self.unit_type = unit_type
        self.alive = True

        # Get stats from config
        stats = UNIT_STATS[unit_type]
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.damage = stats['damage']
        self.speed = stats['speed']
        self.range = stats['range']
        self.attack_speed = stats['attack_speed']

        # Combat properties
        self.target = None
        self.attack_timer = 0
        self.frozen = False
        self.freeze_timer = 0

        # Visual properties
        self.width = 30
        self.height = 40
        self.color = BLUE if team == 'player' else RED

    def update(self, dt, enemies, enemy_castle):
        """Update unit state"""
        if not self.alive:
            return

        # Handle freeze effect
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
            return

        # Update attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

        # Find target
        self.find_target(enemies, enemy_castle)

        # Attack or move
        if self.target:
            distance = self.distance_to(self.target)

            if distance <= self.range:
                # Attack
                if self.attack_timer <= 0:
                    self.attack(self.target)
                    self.attack_timer = self.attack_speed
            else:
                # Move toward target
                self.move_toward(self.target, dt)
        else:
            # Move toward enemy castle
            self.move_toward(enemy_castle, dt)

    def find_target(self, enemies, enemy_castle):
        """Find closest enemy unit or castle"""
        closest = None
        min_dist = float('inf')

        for enemy in enemies:
            if enemy.alive:
                dist = self.distance_to(enemy)
                if dist < min_dist:
                    min_dist = dist
                    closest = enemy

        # If no enemies in reasonable range, target castle
        if min_dist > 400:
            self.target = enemy_castle
        else:
            self.target = closest if closest else enemy_castle

    def move_toward(self, target, dt):
        """Move toward target"""
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Normalize and move
            dx /= distance
            dy /= distance
            self.x += dx * self.speed * dt * 60
            self.y += dy * self.speed * dt * 60

    def attack(self, target):
        """Attack target"""
        target.take_damage(self.damage)

    def take_damage(self, amount):
        """Take damage"""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def freeze(self, duration):
        """Freeze unit for duration"""
        self.frozen = True
        self.freeze_timer = duration

    def distance_to(self, other):
        """Calculate distance to another object"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def draw(self, screen):
        """Draw unit"""
        if not self.alive:
            return

        # Draw unit body
        if self.frozen:
            color = (150, 200, 255)  # Light blue for frozen
        else:
            color = self.color

        pygame.draw.rect(screen, color,
                        (self.x - self.width//2, self.y - self.height,
                         self.width, self.height))

        # Draw HP bar
        if self.hp < self.max_hp:
            bar_width = self.width
            bar_height = 5
            hp_ratio = self.hp / self.max_hp

            # Background (red)
            pygame.draw.rect(screen, RED,
                           (self.x - bar_width//2, self.y - self.height - 10,
                            bar_width, bar_height))
            # Health (green)
            pygame.draw.rect(screen, GREEN,
                           (self.x - bar_width//2, self.y - self.height - 10,
                            bar_width * hp_ratio, bar_height))

        # Draw unit type indicator
        self._draw_type_indicator(screen)

    def _draw_type_indicator(self, screen):
        """Draw a visual indicator of unit type"""
        center_x = self.x
        center_y = self.y - self.height // 2

        if self.unit_type == 'knight':
            # Sword
            pygame.draw.line(screen, YELLOW,
                           (center_x, center_y - 5),
                           (center_x, center_y + 5), 3)
        elif self.unit_type == 'archer':
            # Bow
            pygame.draw.arc(screen, BROWN,
                          (center_x - 5, center_y - 5, 10, 10),
                          -math.pi/4, math.pi/4, 2)
        elif self.unit_type == 'spearman':
            # Spear
            pygame.draw.line(screen, GRAY,
                           (center_x - 5, center_y),
                           (center_x + 5, center_y), 3)
        elif self.unit_type == 'mage':
            # Star
            pygame.draw.circle(screen, YELLOW, (center_x, center_y), 4)
        elif self.unit_type == 'cannon':
            # Circle (cannon ball)
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 5)
        elif self.unit_type == 'hero':
            # Crown
            pygame.draw.polygon(screen, YELLOW, [
                (center_x - 6, center_y),
                (center_x - 3, center_y - 5),
                (center_x, center_y),
                (center_x + 3, center_y - 5),
                (center_x + 6, center_y)
            ])


class Knight(Unit):
    """Melee fighter with balanced stats"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'knight')


class Archer(Unit):
    """Ranged attacker with long range"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'archer')


class Spearman(Unit):
    """Anti-cavalry unit with medium range"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'spearman')


class Mage(Unit):
    """Magic user with high damage but slow attack"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'mage')


class Cannon(Unit):
    """Heavy siege unit with extreme range"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'cannon')


class Hero(Unit):
    """Powerful unique unit"""
    def __init__(self, x, y, team):
        super().__init__(x, y, team, 'hero')
