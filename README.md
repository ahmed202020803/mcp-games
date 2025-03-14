# MCP Games

A game development framework that integrates the Model Context Protocol (MCP) for AI-powered gaming experiences.

## Features

### Core Game Engine
- Complete game object system with components
- Physics system with collision detection
- Rendering system with sprites and particles
- Input handling system
- Sound system for audio playback
- Scene management
- Event system

### AI Integration
- Advanced AI controller with MCP integration
- Memory system for NPCs to remember events and interactions
- Emotion system for realistic NPC behaviors
- Behavior system with state machines
- Dialog generation using AI models
- Decision making based on context and memories

### MCP Features
- AI-powered NPCs and game mechanics
- Procedural content generation
- Interactive storytelling
- Real-time decision making
- Memory and context-aware interactions

## Installation

```bash
# Clone the repository
git clone https://github.com/ahmed202020803/mcp-games.git
cd mcp-games

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Example

```python
from mcp_games.engine import GameEngine
from mcp_games.ai import AIController

# Initialize game engine
engine = GameEngine()

# Create AI controller
ai = AIController(engine)

# Register game objects
player = engine.create_player()
npc = engine.create_npc("villager")

# Set up AI behavior
ai.set_behavior(npc, "friendly_villager")

# Start game loop
engine.start()
```

### Advanced Example

```python
from mcp_games.engine import AdvancedGameEngine
from mcp_games.ai import AdvancedAIController
from mcp_games.physics import Vector3

# Initialize advanced game engine
engine = AdvancedGameEngine(screen_width=1024, screen_height=768)

# Initialize advanced AI controller with MCP API key
ai = AdvancedAIController(engine, mcp_api_key="your-api-key")

# Create player with physics and rendering
player = engine.create_player()
engine.add_collider(player, "sphere", radius=0.5)
engine.add_render_component(player, "sprites/player.png")

# Create NPC with advanced AI
npc = engine.create_npc("villager")
engine.add_collider(npc, "sphere", radius=0.5)
engine.add_render_component(npc, "sprites/villager.png")

# Add memories to NPC
ai.add_memory(
    npc.id,
    "I am a villager living in this area.",
    importance=0.8,
    category="identity"
)

# Set emotions for NPC
ai.update_emotion(npc.id, "happiness", 0.7)

# Create particle effects
particles = engine.create_particle_system(Vector3(0, 1, 0))
particles.start()

# Start game loop
engine.start()
```

## Examples

The repository includes two example games:

1. **Simple Game** (`examples/simple_game.py`): A basic example showing core functionality
2. **Advanced Game** (`examples/advanced_game.py`): A comprehensive example demonstrating all features

To run the advanced example:

```bash
python examples/advanced_game.py
```

Controls:
- WASD: Move player
- ESC: Quit
- P: Pause/Resume
- F1: Toggle debug info

## Project Structure

```
mcp-games/
├── assets/              # Game assets
│   ├── sprites/         # Image files
│   └── sounds/          # Audio files
├── config/              # Configuration files
├── src/                 # Source code
│   ├── engine/          # Game engine core
│   │   ├── physics.py   # Physics system
│   │   └── renderer.py  # Rendering system
│   ├── ai/              # AI integration components
│   │   ├── behavior.py  # Behavior system
│   │   └── advanced_ai.py # Advanced AI with MCP
│   └── utils/           # Utility functions
├── examples/            # Example games and demos
├── docs/                # Documentation
├── tests/               # Test suite
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

## MCP Integration

The framework integrates with the Model Context Protocol (MCP) to provide AI-powered gaming experiences:

- **Dialog Generation**: NPCs can generate contextually relevant dialog based on their memories, emotions, and current situation
- **Decision Making**: AI can make decisions for NPCs based on their personality, memories, and context
- **Memory System**: NPCs remember interactions and events, which influence their future behavior
- **Emotion System**: NPCs have emotional states that evolve over time and affect their behavior

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.