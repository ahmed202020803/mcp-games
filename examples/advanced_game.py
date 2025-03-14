"""
Advanced Game Example using MCP Games
"""

import os
import sys
import logging
import random
import math
import pygame
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.advanced_game_engine import AdvancedGameEngine
from src.engine.physics import Vector3
from src.ai.advanced_ai import AdvancedAIController
from src.ai.behavior import WanderBehavior, FollowBehavior, StateMachineBehavior

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
GAME_TITLE = "MCP Advanced Game Example"

# Asset paths
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets'))
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')

# Create asset directories if they don't exist
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(SOUNDS_DIR, exist_ok=True)

# Create placeholder sprites if they don't exist
def create_placeholder_sprites():
    """Create placeholder sprites for the example"""
    # Player sprite
    player_sprite_path = os.path.join(SPRITES_DIR, 'player.png')
    if not os.path.exists(player_sprite_path):
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 0, 255), (16, 16), 16)
        pygame.image.save(surface, player_sprite_path)
    
    # Villager sprite
    villager_sprite_path = os.path.join(SPRITES_DIR, 'villager.png')
    if not os.path.exists(villager_sprite_path):
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 255, 0), (16, 16), 16)
        pygame.image.save(surface, villager_sprite_path)
    
    # Guard sprite
    guard_sprite_path = os.path.join(SPRITES_DIR, 'guard.png')
    if not os.path.exists(guard_sprite_path):
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 0, 0), (16, 16), 16)
        pygame.image.save(surface, guard_sprite_path)
    
    # Obstacle sprite
    obstacle_sprite_path = os.path.join(SPRITES_DIR, 'obstacle.png')
    if not os.path.exists(obstacle_sprite_path):
        surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surface, (150, 75, 0), (0, 0, 32, 32))
        pygame.image.save(surface, obstacle_sprite_path)

def create_guard_behavior() -> StateMachineBehavior:
    """Create a state machine behavior for guards"""
    behavior = StateMachineBehavior("guard_behavior")
    
    # Define states
    def patrol_state(npc, delta_time):
        """Patrol between waypoints"""
        # Get or create waypoints
        waypoints = npc.get_property("waypoints")
        if not waypoints:
            # Create some random waypoints
            waypoints = [
                (random.uniform(-10, 10), 0, random.uniform(-10, 10)),
                (random.uniform(-10, 10), 0, random.uniform(-10, 10)),
                (random.uniform(-10, 10), 0, random.uniform(-10, 10)),
                (random.uniform(-10, 10), 0, random.uniform(-10, 10))
            ]
            npc.set_property("waypoints", waypoints)
            npc.set_property("current_waypoint", 0)
        
        # Get current waypoint
        current_waypoint = npc.get_property("current_waypoint", 0)
        target = waypoints[current_waypoint]
        
        # Move towards waypoint
        speed = 2.0 * delta_time
        current_pos = Vector3.from_tuple(npc.position)
        target_pos = Vector3.from_tuple(target)
        
        direction = target_pos - current_pos
        distance = direction.magnitude()
        
        if distance < 0.5:
            # Reached waypoint, move to next
            npc.set_property("current_waypoint", (current_waypoint + 1) % len(waypoints))
        else:
            # Move towards waypoint
            direction = direction.normalize()
            new_pos = current_pos + (direction * speed)
            npc.position = new_pos.to_tuple()
    
    def chase_state(npc, delta_time):
        """Chase the player"""
        # Get player
        player = npc.get_property("player")
        if not player:
            return
        
        # Move towards player
        speed = 3.0 * delta_time
        current_pos = Vector3.from_tuple(npc.position)
        player_pos = Vector3.from_tuple(player.position)
        
        direction = player_pos - current_pos
        distance = direction.magnitude()
        
        if distance > 0.1:
            direction = direction.normalize()
            new_pos = current_pos + (direction * speed)
            npc.position = new_pos.to_tuple()
    
    def alert_state(npc, delta_time):
        """Alert state - look around and then chase"""
        # Get alert timer
        alert_timer = npc.get_property("alert_timer", 0)
        alert_timer -= delta_time
        
        if alert_timer <= 0:
            # Timer expired, switch to chase
            npc.set_property("state", "chase")
        else:
            # Look around (rotate in place)
            npc.set_property("alert_timer", alert_timer)
            
            # Simulate looking around by slightly moving
            angle = math.sin(alert_timer * 5) * 0.1
            current_pos = Vector3.from_tuple(npc.position)
            new_pos = Vector3(
                current_pos.x + math.cos(angle) * 0.1,
                current_pos.y,
                current_pos.z + math.sin(angle) * 0.1
            )
            npc.position = new_pos.to_tuple()
    
    # Add states to behavior
    behavior.add_state("patrol", patrol_state)
    behavior.add_state("alert", alert_state)
    behavior.add_state("chase", chase_state)
    
    # Define transitions
    def should_alert(npc):
        """Check if guard should become alert"""
        player = npc.get_property("player")
        if not player:
            return False
        
        # Check distance to player
        current_pos = Vector3.from_tuple(npc.position)
        player_pos = Vector3.from_tuple(player.position)
        distance = current_pos.distance_to(player_pos)
        
        return distance < 5.0 and random.random() < 0.1  # 10% chance per frame when in range
    
    def should_chase(npc):
        """Check if guard should chase player"""
        return npc.get_property("state") == "chase"
    
    def should_patrol(npc):
        """Check if guard should return to patrol"""
        player = npc.get_property("player")
        if not player:
            return True
        
        # Check distance to player
        current_pos = Vector3.from_tuple(npc.position)
        player_pos = Vector3.from_tuple(player.position)
        distance = current_pos.distance_to(player_pos)
        
        return distance > 10.0  # Return to patrol if player is far away
    
    # Add transitions
    behavior.add_transition("patrol", "alert", should_alert)
    behavior.add_transition("alert", "chase", should_chase)
    behavior.add_transition("chase", "patrol", should_patrol)
    
    # Set initial state
    behavior.set_initial_state("patrol")
    
    return behavior

def handle_player_movement(engine, player, delta_time):
    """Handle player movement based on input"""
    input_system = engine.input_system
    
    # Movement speed
    speed = 5.0 * delta_time
    
    # Get current position
    pos = Vector3.from_tuple(player.position)
    
    # Handle keyboard input
    if input_system.is_key_pressed(pygame.K_w):
        pos.z += speed
    if input_system.is_key_pressed(pygame.K_s):
        pos.z -= speed
    if input_system.is_key_pressed(pygame.K_a):
        pos.x -= speed
    if input_system.is_key_pressed(pygame.K_d):
        pos.x += speed
    
    # Update player position
    player.position = pos.to_tuple()

def setup_game(engine, ai_controller):
    """Setup the game world"""
    # Create player
    player = engine.create_player()
    player.position = (0, 0, 0)
    
    # Add player collider
    engine.add_collider(player, "sphere", radius=0.5)
    
    # Add player render component
    player_render = engine.add_render_component(player, os.path.join(SPRITES_DIR, 'player.png'))
    player_render.set_scale(1.5)
    
    # Create villagers
    for i in range(5):
        villager = engine.create_npc("villager")
        villager.position = (random.uniform(-10, 10), 0, random.uniform(-10, 10))
        
        # Add villager collider
        engine.add_collider(villager, "sphere", radius=0.5)
        
        # Add villager render component
        villager_render = engine.add_render_component(villager, os.path.join(SPRITES_DIR, 'villager.png'))
        
        # Set villager behavior
        wander_behavior = WanderBehavior(speed=1.0, radius=5.0)
        ai_controller.register_behavior("wander", wander_behavior)
        ai_controller.set_behavior(villager, "wander")
        
        # Add some memories
        ai_controller.add_memory(
            villager.id,
            f"I am a villager living in this area. I like to wander around.",
            importance=0.8,
            category="identity"
        )
        
        ai_controller.add_memory(
            villager.id,
            f"I saw a player character earlier today.",
            importance=0.5,
            category="observation"
        )
        
        # Set initial emotions
        ai_controller.update_emotion(villager.id, "happiness", random.uniform(0.5, 0.9))
    
    # Create guards
    for i in range(3):
        guard = engine.create_npc("guard")
        guard.position = (random.uniform(-15, 15), 0, random.uniform(-15, 15))
        
        # Add guard collider
        engine.add_collider(guard, "sphere", radius=0.6)
        
        # Add guard render component
        guard_render = engine.add_render_component(guard, os.path.join(SPRITES_DIR, 'guard.png'))
        guard_render.set_scale(1.2)
        
        # Set guard properties
        guard.set_property("player", player)
        guard.set_property("state", "patrol")
        
        # Set guard behavior
        guard_behavior = create_guard_behavior()
        ai_controller.register_behavior(f"guard_behavior_{i}", guard_behavior)
        ai_controller.set_behavior(guard, f"guard_behavior_{i}")
        
        # Add some memories
        ai_controller.add_memory(
            guard.id,
            f"I am a guard patrolling this area. I must protect it from intruders.",
            importance=0.9,
            category="identity"
        )
        
        ai_controller.add_memory(
            guard.id,
            f"I've been ordered to capture any suspicious characters.",
            importance=0.7,
            category="orders"
        )
        
        # Set initial emotions
        ai_controller.update_emotion(guard.id, "trust", 0.3)
        ai_controller.update_emotion(guard.id, "anger", 0.4)
    
    # Create obstacles
    for i in range(10):
        obstacle_id = f"obstacle_{i}"
        obstacle = GameObject(obstacle_id, "obstacle")
        obstacle.position = (random.uniform(-20, 20), 0, random.uniform(-20, 20))
        
        # Add to engine
        engine.add_object(obstacle)
        
        # Add obstacle collider
        engine.add_collider(obstacle, "box", size=Vector3(2.0, 2.0, 2.0))
        
        # Add obstacle render component
        obstacle_render = engine.add_render_component(obstacle, os.path.join(SPRITES_DIR, 'obstacle.png'))
        obstacle_render.set_scale(2.0)
    
    # Setup camera
    camera = engine.render_system.camera
    camera.position = Vector3(0, 20, -20)
    camera.look_at(Vector3(0, 0, 0))
    
    # Register player movement handler
    engine.register_event_handler("update", lambda delta_time: handle_player_movement(engine, player, delta_time))
    
    # Create a particle system for effect
    particles = engine.create_particle_system(Vector3(0, 1, 0))
    particles.start()
    
    return player

def main():
    """Main function"""
    # Get MCP API key from environment
    mcp_api_key = os.getenv('MCP_API_KEY')
    
    # Create placeholder sprites
    create_placeholder_sprites()
    
    # Initialize game engine
    engine = AdvancedGameEngine(SCREEN_WIDTH, SCREEN_HEIGHT, GAME_TITLE)
    
    # Initialize AI controller
    ai_controller = AdvancedAIController(engine, mcp_api_key)
    
    # Setup game
    player = setup_game(engine, ai_controller)
    
    # Start game
    print("Starting advanced game example...")
    print("Controls:")
    print("  WASD - Move player")
    print("  ESC - Quit")
    print("  P - Pause/Resume")
    print("  F1 - Toggle debug info")
    
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    
if __name__ == "__main__":
    main()