"""
Game Engine Core Implementation
"""

import time
import logging
from typing import Dict, List, Any, Optional

class GameObject:
    """Base class for all game objects"""
    
    def __init__(self, object_id: str, object_type: str):
        self.id = object_id
        self.type = object_type
        self.position = (0, 0, 0)
        self.rotation = (0, 0, 0)
        self.scale = (1, 1, 1)
        self.properties = {}
        
    def update(self, delta_time: float):
        """Update game object state"""
        pass
        
    def render(self):
        """Render game object"""
        pass
        
    def set_property(self, key: str, value: Any):
        """Set a custom property"""
        self.properties[key] = value
        
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a custom property"""
        return self.properties.get(key, default)


class Player(GameObject):
    """Player character in the game"""
    
    def __init__(self, player_id: str):
        super().__init__(player_id, "player")
        self.health = 100
        self.inventory = []
        
    def update(self, delta_time: float):
        """Update player state"""
        # Player-specific update logic
        pass


class NPC(GameObject):
    """Non-player character in the game"""
    
    def __init__(self, npc_id: str, npc_type: str):
        super().__init__(npc_id, f"npc_{npc_type}")
        self.health = 100
        self.behavior = None
        self.dialog = []
        
    def update(self, delta_time: float):
        """Update NPC state"""
        # NPC-specific update logic
        if self.behavior:
            self.behavior.update(self, delta_time)


class GameEngine:
    """Main game engine class"""
    
    def __init__(self):
        self.objects: Dict[str, GameObject] = {}
        self.running = False
        self.last_update_time = 0
        self.logger = logging.getLogger("mcp_games.engine")
        
    def create_player(self) -> Player:
        """Create a new player object"""
        player_id = f"player_{len([o for o in self.objects.values() if isinstance(o, Player)]) + 1}"
        player = Player(player_id)
        self.objects[player_id] = player
        return player
        
    def create_npc(self, npc_type: str) -> NPC:
        """Create a new NPC object"""
        npc_id = f"npc_{npc_type}_{len([o for o in self.objects.values() if isinstance(o, NPC)]) + 1}"
        npc = NPC(npc_id, npc_type)
        self.objects[npc_id] = npc
        return npc
        
    def get_object(self, object_id: str) -> Optional[GameObject]:
        """Get a game object by ID"""
        return self.objects.get(object_id)
        
    def update(self, delta_time: float):
        """Update all game objects"""
        for obj in self.objects.values():
            obj.update(delta_time)
            
    def render(self):
        """Render all game objects"""
        for obj in self.objects.values():
            obj.render()
            
    def start(self):
        """Start the game loop"""
        self.running = True
        self.last_update_time = time.time()
        
        self.logger.info("Game engine started")
        
        try:
            while self.running:
                current_time = time.time()
                delta_time = current_time - self.last_update_time
                self.last_update_time = current_time
                
                self.update(delta_time)
                self.render()
                
                # Cap frame rate
                time.sleep(max(0, 1/60 - (time.time() - current_time)))
                
        except KeyboardInterrupt:
            self.logger.info("Game engine stopped by user")
        finally:
            self.running = False
            self.logger.info("Game engine stopped")
            
    def stop(self):
        """Stop the game loop"""
        self.running = False