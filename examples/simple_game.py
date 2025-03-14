"""
Simple Game Example using MCP Games
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine import GameEngine
from src.ai import AIController, Behavior
from src.ai.behavior import WanderBehavior, FollowBehavior

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Main function"""
    # Get MCP API key from environment
    mcp_api_key = os.getenv('MCP_API_KEY')
    
    # Initialize game engine
    engine = GameEngine()
    
    # Initialize AI controller
    ai = AIController(engine, mcp_api_key)
    
    # Create player
    player = engine.create_player()
    player.position = (0, 0, 0)
    
    # Create NPCs
    villager = engine.create_npc("villager")
    villager.position = (5, 0, 5)
    villager.set_property('engine', engine)
    
    guard = engine.create_npc("guard")
    guard.position = (-5, 0, -5)
    guard.set_property('engine', engine)
    
    # Create behaviors
    wander_behavior = WanderBehavior(speed=0.5, radius=3.0)
    follow_behavior = FollowBehavior(target_id=player.id, min_distance=2.0)
    
    # Register behaviors
    ai.register_behavior("wander", wander_behavior)
    ai.register_behavior("follow_player", follow_behavior)
    
    # Set behaviors
    ai.set_behavior(villager, "wander")
    ai.set_behavior(guard, "follow_player")
    
    # Start game
    print("Starting simple game example...")
    print("Press Ctrl+C to exit")
    
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    
if __name__ == "__main__":
    main()