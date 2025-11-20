# Castle Strategy Game

A 2D real-time strategy game inspired by **Anakin's Castle Duels**, a classic Czech game. Two castles battle against each other, and players must produce units and manage resources to destroy the enemy castle while defending their own.

## 🎮 Play Online

**[Play the game in your browser!](https://aiforgewolf.github.io/rpgjiri/)** - No installation required!

The game is automatically built and deployed to GitHub Pages using Pygbag.

![Game Screenshot](screenshot.png)

## Features

- **6 Different Unit Types**:
  - **Knight**: Balanced melee fighter
  - **Archer**: Long-range attacker
  - **Spearman**: Medium-range fighter
  - **Mage**: High damage magic user with slow attack speed
  - **Cannon**: Extreme range siege weapon
  - **Hero**: Powerful champion unit

- **Resource Management**:
  - Gold accumulates over time
  - Build mines to increase gold generation
  - Unit costs increase with each unit produced (progressive pricing)

- **Spell System**:
  - **Fireball**: Damages multiple enemy units
  - **Heal**: Restores castle health
  - **Gold Boost**: Grants bonus gold
  - **Freeze**: Temporarily freezes enemy units

- **Strategic Gameplay**:
  - Units automatically move toward and attack enemies
  - Different unit ranges and attack speeds create strategic depth
  - AI opponent with varying strategies (aggressive, defensive, balanced)

## Desktop Installation (Optional)

You can also run the game locally on your desktop!

### Requirements
- Python 3.7 or higher
- Pygame 2.5.0 or higher

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

## How to Play

### Objective
Destroy the enemy castle while defending your own!

### Controls

#### Unit Production (Keyboard)
- **1** - Produce Knight (500g base cost)
- **2** - Produce Archer (300g base cost)
- **3** - Produce Spearman (400g base cost)
- **4** - Produce Mage (800g base cost)
- **5** - Produce Cannon (1200g base cost)
- **6** - Produce Hero (1500g base cost)

#### Buildings
- **M** - Build Mine (400g) - Increases gold generation by +3/second

#### Spells
- **F** - Fireball (600g) - Damages up to 3 enemy units
- **H** - Heal (500g) - Restores 200 castle HP
- **G** - Gold Boost (400g) - Grants 500 bonus gold
- **Z** - Freeze (700g) - Freezes all enemy units for 5 seconds

#### Mouse Controls
- Click on buttons in the UI to produce units or cast spells

### Gameplay Tips

1. **Start with Knights**: They're balanced and affordable in the early game

2. **Build Mines Early**: Increasing your gold generation gives you a long-term advantage

3. **Mix Your Units**:
   - Use Archers behind your lines for ranged support
   - Knights and Spearmen form your front line
   - Cannons can attack from extreme range
   - Mages deal high damage but attack slowly

4. **Watch Your Gold**: Unit costs increase exponentially. The first Knight costs 500g, the second costs 750g, the third costs 1125g, etc.

5. **Use Spells Wisely**: Spells have cooldowns and can turn the tide of battle
   - Use Fireball when enemy has many units grouped
   - Heal when your castle is taking damage
   - Freeze to stop a large enemy push

6. **Counter the Enemy**:
   - If the enemy uses many melee units, produce Archers
   - If the enemy stays defensive with Archers, use Cannons
   - Heroes are powerful but expensive - save them for critical moments

## Game Mechanics

### Resource System
- Base gold generation: 5 gold/second
- Each mine adds: +3 gold/second
- Gold accumulates continuously

### Unit Cost Scaling
- Base cost × (1.5 ^ units_of_that_type)
- Example: If you've produced 3 Knights, the 4th will cost: 500 × 1.5³ = 1687.5g

### Combat
- Units automatically engage enemies in range
- Melee units must get close to attack
- Ranged units attack from distance
- Units prioritize enemy units over the castle when enemies are nearby

### AI Behavior
- AI makes decisions every 2 seconds
- Switches between strategies: aggressive, defensive, or balanced
- Builds mines periodically
- Casts spells when it has enough gold
- Produces units based on current strategy

## File Structure

```
rpgjiri/
├── main.py              # Entry point
├── game.py              # Main game loop and logic
├── castle.py            # Castle class
├── units.py             # Unit classes
├── config.py            # Game configuration and constants
├── requirements.txt     # Python dependencies
├── index.html           # Web version landing page
├── .github/workflows/   # GitHub Actions for deployment
└── README.md            # This file
```

## Deploying to GitHub Pages

This game is configured to automatically deploy to GitHub Pages using Pygbag when you push to the repository.

### Setup Instructions

1. **Enable GitHub Pages** in your repository:
   - Go to Settings → Pages
   - Under "Build and deployment", select "GitHub Actions" as the source

2. **Push your code** to the repository:
   ```bash
   git push origin main
   ```

3. **Wait for deployment**:
   - Go to the "Actions" tab in your GitHub repository
   - Watch the "Deploy to GitHub Pages" workflow complete
   - Once finished, your game will be live at: `https://[username].github.io/[repository-name]/`

4. **Access your game**:
   - The game will be playable in any modern web browser
   - No installation required for players!

### Local Web Testing

To test the web version locally before deploying:

```bash
# Install pygbag
pip install pygbag

# Build and serve locally
python -m pygbag --build .

# Or run in live mode (auto-rebuild on changes)
python -m pygbag .
```

Then open your browser to `http://localhost:8000`

## Customization

You can modify game parameters in `config.py`:

- **Screen size**: `SCREEN_WIDTH`, `SCREEN_HEIGHT`
- **Starting resources**: `STARTING_GOLD`, `CASTLE_STARTING_HP`
- **Unit stats**: `UNIT_STATS` dictionary
- **Unit costs**: `UNIT_COSTS` dictionary
- **Spell effects**: `SPELLS` dictionary
- **AI difficulty**: `AI_REACTION_TIME`, `AI_GOLD_SAVE_THRESHOLD`

## Credits

Inspired by **Anakin's Castle Duels** by Anakin (Czech Republic)

Original game description (Czech):
> Vynikající strategická hra původem z Česka. Jedná se komplexní a zábavnou hru o dobývání hradů. Oba protivníci mají na své straně hrad s určitým počtem životů a snaží se jej uchránit před útoky soupeře a naopak vlastními silami zničit ten jeho.

Translation: "An excellent strategy game from the Czech Republic. It's a complex and entertaining game about conquering castles. Both opponents have a castle with a certain number of hit points and try to protect it from enemy attacks while destroying the enemy castle with their own forces."

## License

This project is created as a tribute to the original Anakin's Castle Duels. Feel free to modify and share!

## Troubleshooting

### Game won't start
- Make sure Pygame is installed: `pip install pygame`
- Check Python version: `python --version` (should be 3.7+)

### Performance issues
- Lower the FPS in `config.py`
- Reduce screen resolution in `config.py`

### Game is too easy/hard
- Adjust AI settings in `config.py`
- Modify unit costs and stats

## Future Enhancements

Potential features to add:
- Multiple difficulty levels
- Campaign mode with missions
- More unit types (catapults, dragons, etc.)
- Walls and defensive structures
- Multiplayer support
- Sound effects and music
- Better graphics and animations
- Unit upgrades
- Different castle types

Enjoy the game! May your castle stand strong! 🏰⚔️
