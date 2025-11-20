#!/usr/bin/env python3
"""
Castle Strategy Game
Inspired by Anakin's Castle Duels

A 2D real-time strategy game where two castles battle against each other.
Players can produce various units and cast spells to defeat the enemy.
"""

import asyncio
from game import Game


async def main():
    """Main entry point"""
    game = Game()
    await game.run()


if __name__ == '__main__':
    asyncio.run(main())
