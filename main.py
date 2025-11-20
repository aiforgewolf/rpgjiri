#!/usr/bin/env python3
"""
Castle Strategy Game
Inspired by Anakin's Castle Duels

A 2D real-time strategy game where two castles battle against each other.
Players can produce various units and cast spells to defeat the enemy.
"""

from game import Game


def main():
    """Main entry point"""
    game = Game()
    game.run()


if __name__ == '__main__':
    main()
