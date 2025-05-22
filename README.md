# 🧠 CypherCore

**Created by**: Ahnaf Ashique Adi  
**Built for**: Amazon Q CLI Game Challenge (May–June 2025)  
**Tech Stack**: Python + Pygame  

![CypherCore Logo](https://via.placeholder.com/800x200/0a0a0a/00ff00?text=CypherCore)

## 💡 Game Concept

**CypherCore** is a terminal-style, retro-futuristic hacking simulation game where you, the player, must infiltrate the Core of a digital fortress. Solve logic-based puzzles, decrypt memory structures, and defeat time-based traps across four distinct levels — all wrapped in a slick Matrix aesthetic with a cyan-purple color scheme.

## 🎮 Gameplay

Navigate through four increasingly difficult levels:

1. **Binary Maze**: Navigate a maze of 0s and 1s, avoiding traps that reset your position
2. **Logic Gate Puzzle**: Arrange and toggle logic gates to complete a complex circuit
3. **Memory Decryption**: Match pairs of memory sectors in a memory-based challenge
4. **Core Breach**: Time your clicks to hit rotating nodes in sequence

## ✨ Features

- Dynamic Matrix-style falling code background with cyan-purple gradient
- Periodic "CypherCore" message display in the Matrix background
- Animated ASCII art intro with glitch effects
- Smooth transitions between game states
- Procedurally generated sound effects
- Four unique puzzle mechanics
- Performance monitoring (toggle FPS display with F3)

## 🔧 Installation

### Requirements
- Python 3.x
- Pygame

### Setup
```bash
# Clone the repository
git clone https://github.com/ahnafashiqueadi/cypher_core.git
cd cypher_core

# Install dependencies
pip install pygame

# Run the game
python main.py
```

## 🎯 Controls

- **Arrow Keys**: Navigate menus and control player movement
- **Enter/Return**: Select menu options
- **Mouse**: Interact with puzzles (clicking on tiles, gates, nodes)
- **F3**: Toggle FPS display

## 🏆 Challenge

Can you breach all four levels of security and reach the core? Each level tests a different skill:
- **Navigation**: Find your way through the Binary Maze
- **Logic**: Solve the Logic Gate Puzzle
- **Memory**: Match pairs in Memory Decryption
- **Timing**: Hit the nodes in sequence in Core Breach

## 📝 Development Challenges & Solutions

### 1. Memory Game Click Issue
**Problem**: The Memory Decryption game wasn't properly handling clicks, causing tiles to remain revealed when they shouldn't.

**Solution**: Rewrote the click handling logic to properly track selected tiles and reset them when appropriate. Added proper state management to ensure tiles are only clickable at the right times.

### 2. Logic Gate Puzzle Complexity
**Problem**: The initial Logic Gate puzzle was too simple and didn't provide enough challenge.

**Solution**: 
- Added multiple puzzle variants that are randomly selected
- Increased complexity with additional gates (XOR, NAND implementations)
- Created more sophisticated circuit designs requiring deeper understanding

### 3. Audio Implementation
**Problem**: Implementing audio without external dependencies was challenging.

**Solution**: Created a simple audio engine that generates basic sound effects using pygame's built-in capabilities. Added fallback mechanisms to ensure the game runs even if sound generation fails.

### 4. Matrix Background Glitches
**Problem**: The Matrix background effect would crash with out-of-bounds errors during glitch effects.

**Solution**: Added proper boundary checking and error handling to ensure the glitch effects never attempt to access pixels outside the screen boundaries.

### 5. Performance Optimization
**Problem**: The game would slow down on some systems due to inefficient rendering.

**Solution**:
- Implemented frame time tracking to monitor performance
- Added FPS display toggle (F3 key)
- Optimized matrix effect rendering by limiting the number of particles based on screen size
- Added proper surface management to reduce memory usage

### 6. Level Timer Consistency
**Problem**: Level timers were inconsistent, making some levels too difficult to complete.

**Solution**: Standardized all level timers to 120 seconds, providing a consistent experience across all puzzles while still maintaining challenge.

## 🔮 Future Enhancements

- Additional levels with new mechanics
- High score system
- More complex procedural music generation
- Additional visual effects
- Level editor

## 📜 License

This project is available for educational purposes.

---

*"The only way to learn the rules of this game is to play it." - CypherCore*
