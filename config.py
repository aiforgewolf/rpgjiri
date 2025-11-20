"""
Game Configuration
Castle Strategy Game - Inspired by Anakin's Castle Duels
"""

# Screen settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)
YELLOW = (200, 200, 50)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
LIGHT_BLUE = (135, 206, 235)
BROWN = (139, 69, 19)
DARK_GREEN = (34, 139, 34)

# Game settings
STARTING_GOLD = 1000
GOLD_PER_SECOND = 5
CASTLE_STARTING_HP = 10000

# Castle positions
PLAYER_CASTLE_X = 100
ENEMY_CASTLE_X = 1300
CASTLE_Y = 600
CASTLE_WIDTH = 150
CASTLE_HEIGHT = 250

# Unit base costs
UNIT_COSTS = {
    'knight': 500,
    'archer': 300,
    'spearman': 400,
    'mage': 800,
    'cannon': 1200,
    'hero': 1500
}

# Cost multiplier per unit on field
COST_MULTIPLIER = 1.5

# Mine cost
MINE_COST = 400
MINE_GOLD_BONUS = 3

# Unit stats: {hp, damage, speed, range, attack_speed}
UNIT_STATS = {
    'knight': {'hp': 150, 'damage': 25, 'speed': 2.0, 'range': 30, 'attack_speed': 1.0},
    'archer': {'hp': 80, 'damage': 20, 'speed': 1.5, 'range': 250, 'attack_speed': 1.5},
    'spearman': {'hp': 120, 'damage': 30, 'speed': 1.8, 'range': 50, 'attack_speed': 1.2},
    'mage': {'hp': 100, 'damage': 50, 'speed': 1.2, 'range': 200, 'attack_speed': 2.5},
    'cannon': {'hp': 200, 'damage': 100, 'speed': 0.8, 'range': 350, 'attack_speed': 3.0},
    'hero': {'hp': 300, 'damage': 60, 'speed': 2.5, 'range': 40, 'attack_speed': 0.8}
}

# Spell costs and effects
SPELLS = {
    'fireball': {'cost': 600, 'damage': 150, 'cooldown': 10},
    'heal': {'cost': 500, 'amount': 200, 'cooldown': 15},
    'gold_boost': {'cost': 400, 'amount': 500, 'cooldown': 20},
    'freeze': {'cost': 700, 'duration': 5, 'cooldown': 25}
}

# AI settings
AI_REACTION_TIME = 2.0  # seconds
AI_GOLD_SAVE_THRESHOLD = 800
