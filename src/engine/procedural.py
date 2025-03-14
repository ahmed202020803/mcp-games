"""
Procedural Level Generation System for MCP Games
"""

import random
import math
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass

from .physics import Vector3

@dataclass
class Room:
    """Represents a room in a procedural level"""
    position: Vector3
    width: float
    height: float
    depth: float
    room_type: str = "default"
    connections: List[int] = None
    
    def __post_init__(self):
        if self.connections is None:
            self.connections = []
    
    @property
    def center(self) -> Vector3:
        """Get the center position of the room"""
        return self.position
    
    @property
    def min_bounds(self) -> Vector3:
        """Get the minimum bounds of the room"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        return Vector3(
            self.position.x - half_width,
            self.position.y - half_height,
            self.position.z - half_depth
        )
    
    @property
    def max_bounds(self) -> Vector3:
        """Get the maximum bounds of the room"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        return Vector3(
            self.position.x + half_width,
            self.position.y + half_height,
            self.position.z + half_depth
        )
    
    def intersects(self, other: 'Room', buffer: float = 1.0) -> bool:
        """Check if this room intersects with another room"""
        # Add buffer to avoid rooms being too close
        min_a = self.min_bounds
        max_a = self.max_bounds
        min_b = other.min_bounds
        max_b = other.max_bounds
        
        # Adjust bounds with buffer
        min_a = Vector3(min_a.x - buffer, min_a.y - buffer, min_a.z - buffer)
        max_a = Vector3(max_a.x + buffer, max_a.y + buffer, max_a.z + buffer)
        
        # Check for intersection
        return (
            min_a.x <= max_b.x and max_a.x >= min_b.x and
            min_a.y <= max_b.y and max_a.y >= min_b.y and
            min_a.z <= max_b.z and max_a.z >= min_b.z
        )
    
    def distance_to(self, other: 'Room') -> float:
        """Calculate distance between room centers"""
        return self.center.distance_to(other.center)


@dataclass
class Corridor:
    """Represents a corridor connecting two rooms"""
    start_room_idx: int
    end_room_idx: int
    width: float = 2.0
    height: float = 3.0
    path_points: List[Vector3] = None
    
    def __post_init__(self):
        if self.path_points is None:
            self.path_points = []


class ProceduralLevelGenerator:
    """Generates procedural levels with rooms and corridors"""
    
    def __init__(self, engine: Any = None):
        self.engine = engine
        self.rooms: List[Room] = []
        self.corridors: List[Corridor] = []
        self.logger = logging.getLogger("mcp_games.engine.procedural")
        
        # Default room types and their probabilities
        self.room_types = {
            "default": 0.5,
            "treasure": 0.1,
            "enemy": 0.25,
            "boss": 0.05,
            "shop": 0.1
        }
        
        # Room size ranges
        self.min_room_size = 5.0
        self.max_room_size = 15.0
        
        # Level bounds
        self.level_bounds = (
            Vector3(-50, -10, -50),  # Min bounds
            Vector3(50, 10, 50)      # Max bounds
        )
    
    def generate_level(self, num_rooms: int = 10, 
                       min_room_size: Optional[float] = None,
                       max_room_size: Optional[float] = None,
                       room_types: Optional[Dict[str, float]] = None) -> Tuple[List[Room], List[Corridor]]:
        """Generate a procedural level with rooms and corridors"""
        # Clear existing data
        self.rooms = []
        self.corridors = []
        
        # Set parameters
        if min_room_size is not None:
            self.min_room_size = min_room_size
        if max_room_size is not None:
            self.max_room_size = max_room_size
        if room_types is not None:
            self.room_types = room_types
        
        # Generate rooms
        self._generate_rooms(num_rooms)
        
        # Connect rooms
        self._connect_rooms()
        
        return self.rooms, self.corridors
    
    def _generate_rooms(self, num_rooms: int):
        """Generate random rooms"""
        attempts = 0
        max_attempts = num_rooms * 10  # Limit attempts to avoid infinite loops
        
        while len(self.rooms) < num_rooms and attempts < max_attempts:
            # Generate random room size
            width = random.uniform(self.min_room_size, self.max_room_size)
            height = random.uniform(self.min_room_size / 2, self.max_room_size / 2)
            depth = random.uniform(self.min_room_size, self.max_room_size)
            
            # Generate random position within level bounds
            min_bounds, max_bounds = self.level_bounds
            x = random.uniform(min_bounds.x + width/2, max_bounds.x - width/2)
            y = random.uniform(min_bounds.y + height/2, max_bounds.y - height/2)
            z = random.uniform(min_bounds.z + depth/2, max_bounds.z - depth/2)
            
            position = Vector3(x, y, z)
            
            # Select room type based on probabilities
            room_type = self._select_room_type()
            
            # Create new room
            new_room = Room(position, width, height, depth, room_type)
            
            # Check for intersections with existing rooms
            if not any(new_room.intersects(room) for room in self.rooms):
                self.rooms.append(new_room)
                self.logger.debug(f"Added {room_type} room at {position}")
            
            attempts += 1
        
        if attempts >= max_attempts:
            self.logger.warning(f"Reached maximum attempts ({max_attempts}) when generating rooms")
    
    def _select_room_type(self) -> str:
        """Select a room type based on probabilities"""
        r = random.random()
        cumulative = 0
        
        for room_type, probability in self.room_types.items():
            cumulative += probability
            if r <= cumulative:
                return room_type
        
        # Default fallback
        return "default"
    
    def _connect_rooms(self):
        """Connect rooms with corridors using minimum spanning tree"""
        if len(self.rooms) < 2:
            return
        
        # Calculate distances between all rooms
        edges = []
        for i in range(len(self.rooms)):
            for j in range(i+1, len(self.rooms)):
                distance = self.rooms[i].distance_to(self.rooms[j])
                edges.append((i, j, distance))
        
        # Sort edges by distance
        edges.sort(key=lambda x: x[2])
        
        # Minimum spanning tree (Kruskal's algorithm)
        parent = list(range(len(self.rooms)))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            parent[find(x)] = find(y)
        
        mst_edges = []
        for i, j, _ in edges:
            if find(i) != find(j):
                union(i, j)
                mst_edges.append((i, j))
                
                # Add connection to rooms
                self.rooms[i].connections.append(j)
                self.rooms[j].connections.append(i)
        
        # Create corridors for MST edges
        for start_idx, end_idx in mst_edges:
            corridor = self._create_corridor(start_idx, end_idx)
            self.corridors.append(corridor)
        
        # Add some additional corridors for loops (about 10% of MST edges)
        num_extra = max(1, int(len(mst_edges) * 0.1))
        extra_edges = [e for e in edges if (e[0], e[1]) not in mst_edges and (e[1], e[0]) not in mst_edges]
        
        if extra_edges:
            extra_edges = sorted(extra_edges, key=lambda x: x[2])[:num_extra]
            
            for i, j, _ in extra_edges:
                corridor = self._create_corridor(i, j)
                self.corridors.append(corridor)
                
                # Add connection to rooms
                self.rooms[i].connections.append(j)
                self.rooms[j].connections.append(i)
    
    def _create_corridor(self, start_idx: int, end_idx: int) -> Corridor:
        """Create a corridor between two rooms"""
        start_room = self.rooms[start_idx]
        end_room = self.rooms[end_idx]
        
        # Create basic corridor
        corridor = Corridor(start_idx, end_idx)
        
        # Generate path points
        start_pos = start_room.center
        end_pos = end_room.center
        
        # Simple L-shaped path
        # First go along X axis
        mid_x = end_pos.x
        mid_y = start_pos.y
        mid_z = start_pos.z
        
        # Then go along Z axis
        corridor.path_points = [
            start_pos,
            Vector3(mid_x, mid_y, mid_z),
            end_pos
        ]
        
        return corridor
    
    def instantiate_level(self, engine: Any = None) -> Dict[str, List[Any]]:
        """Instantiate the generated level in the game engine"""
        if engine is None:
            engine = self.engine
        
        if engine is None:
            self.logger.error("No game engine provided for instantiation")
            return {}
        
        created_objects = {
            "rooms": [],
            "corridors": [],
            "decorations": []
        }
        
        # Instantiate rooms
        for i, room in enumerate(self.rooms):
            # Create room object
            room_id = f"room_{i}"
            room_obj = engine.GameObject(room_id, f"room_{room.room_type}")
            room_obj.position = room.center.to_tuple()
            
            # Add to engine
            engine.add_object(room_obj)
            
            # Add collider for walls
            engine.add_collider(room_obj, "box", size=Vector3(room.width, room.height, room.depth))
            
            # Add render component based on room type
            color = self._get_room_color(room.room_type)
            render_comp = engine.add_render_component(room_obj)
            render_comp.set_color(color)
            
            created_objects["rooms"].append(room_obj)
            
            # Add decorations based on room type
            decorations = self._add_room_decorations(engine, room, room_obj)
            created_objects["decorations"].extend(decorations)
        
        # Instantiate corridors
        for i, corridor in enumerate(self.corridors):
            # Create corridor segments
            for j in range(len(corridor.path_points) - 1):
                start = corridor.path_points[j]
                end = corridor.path_points[j + 1]
                
                # Calculate midpoint and dimensions
                mid = (start + end) / 2
                
                # Calculate length and direction
                direction = end - start
                length = direction.magnitude()
                
                # Create corridor segment
                corridor_id = f"corridor_{i}_{j}"
                corridor_obj = engine.GameObject(corridor_id, "corridor")
                corridor_obj.position = mid.to_tuple()
                
                # Add to engine
                engine.add_object(corridor_obj)
                
                # Add collider
                engine.add_collider(corridor_obj, "box", 
                                   size=Vector3(
                                       max(corridor.width, abs(direction.x)),
                                       corridor.height,
                                       max(corridor.width, abs(direction.z))
                                   ))
                
                # Add render component
                render_comp = engine.add_render_component(corridor_obj)
                render_comp.set_color((100, 100, 100))  # Gray corridors
                
                created_objects["corridors"].append(corridor_obj)
        
        return created_objects
    
    def _get_room_color(self, room_type: str) -> Tuple[int, int, int]:
        """Get color for room based on type"""
        colors = {
            "default": (200, 200, 200),  # Light gray
            "treasure": (255, 215, 0),   # Gold
            "enemy": (200, 0, 0),        # Red
            "boss": (128, 0, 128),       # Purple
            "shop": (0, 128, 128)        # Teal
        }
        return colors.get(room_type, (200, 200, 200))
    
    def _add_room_decorations(self, engine: Any, room: Room, room_obj: Any) -> List[Any]:
        """Add decorations to a room based on its type"""
        decorations = []
        
        # Get room bounds
        min_bounds = room.min_bounds
        max_bounds = room.max_bounds
        
        # Add decorations based on room type
        if room.room_type == "treasure":
            # Add treasure chest in center
            chest_id = f"chest_{room_obj.id}"
            chest = engine.GameObject(chest_id, "treasure_chest")
            chest.position = room.center.to_tuple()
            
            # Add to engine
            engine.add_object(chest)
            
            # Add collider
            engine.add_collider(chest, "box", size=Vector3(1.0, 1.0, 1.0))
            
            # Add render component
            render_comp = engine.add_render_component(chest)
            render_comp.set_color((255, 215, 0))  # Gold
            
            decorations.append(chest)
            
        elif room.room_type == "enemy":
            # Add some enemies
            num_enemies = random.randint(2, 5)
            
            for i in range(num_enemies):
                enemy_id = f"enemy_{room_obj.id}_{i}"
                enemy = engine.GameObject(enemy_id, "enemy")
                
                # Random position within room
                x = random.uniform(min_bounds.x + 1, max_bounds.x - 1)
                z = random.uniform(min_bounds.z + 1, max_bounds.z - 1)
                enemy.position = (x, room.center.y, z)
                
                # Add to engine
                engine.add_object(enemy)
                
                # Add collider
                engine.add_collider(enemy, "sphere", radius=0.5)
                
                # Add render component
                render_comp = engine.add_render_component(enemy)
                render_comp.set_color((200, 0, 0))  # Red
                
                decorations.append(enemy)
                
        elif room.room_type == "boss":
            # Add boss in center
            boss_id = f"boss_{room_obj.id}"
            boss = engine.GameObject(boss_id, "boss")
            boss.position = room.center.to_tuple()
            
            # Add to engine
            engine.add_object(boss)
            
            # Add collider
            engine.add_collider(boss, "sphere", radius=1.5)
            
            # Add render component
            render_comp = engine.add_render_component(boss)
            render_comp.set_color((128, 0, 128))  # Purple
            render_comp.set_scale(2.0)
            
            decorations.append(boss)
            
        elif room.room_type == "shop":
            # Add shopkeeper
            shop_id = f"shopkeeper_{room_obj.id}"
            shopkeeper = engine.GameObject(shop_id, "shopkeeper")
            shopkeeper.position = room.center.to_tuple()
            
            # Add to engine
            engine.add_object(shopkeeper)
            
            # Add collider
            engine.add_collider(shopkeeper, "sphere", radius=0.5)
            
            # Add render component
            render_comp = engine.add_render_component(shopkeeper)
            render_comp.set_color((0, 128, 128))  # Teal
            
            decorations.append(shopkeeper)
            
            # Add some items for sale
            num_items = random.randint(2, 4)
            
            for i in range(num_items):
                item_id = f"item_{room_obj.id}_{i}"
                item = engine.GameObject(item_id, "shop_item")
                
                # Position in a circle around shopkeeper
                angle = (i / num_items) * 2 * math.pi
                radius = 2.0
                x = room.center.x + math.cos(angle) * radius
                z = room.center.z + math.sin(angle) * radius
                item.position = (x, room.center.y, z)
                
                # Add to engine
                engine.add_object(item)
                
                # Add collider
                engine.add_collider(item, "box", size=Vector3(0.5, 0.5, 0.5))
                
                # Add render component
                render_comp = engine.add_render_component(item)
                render_comp.set_color((0, 200, 200))  # Light teal
                
                decorations.append(item)
        
        return decorations


class MCPLevelGenerator(ProceduralLevelGenerator):
    """Level generator that uses MCP for enhanced procedural generation"""
    
    def __init__(self, engine: Any = None, mcp_client: Any = None):
        super().__init__(engine)
        self.mcp_client = mcp_client
        
    def generate_themed_level(self, theme: str, num_rooms: int = 10) -> Tuple[List[Room], List[Corridor]]:
        """Generate a level with a specific theme using MCP"""
        if not self.mcp_client:
            self.logger.warning("No MCP client provided, falling back to standard generation")
            return self.generate_level(num_rooms)
        
        try:
            # Get theme parameters from MCP
            theme_params = self._get_theme_parameters(theme)
            
            # Generate level with theme parameters
            return self.generate_level(
                num_rooms=num_rooms,
                min_room_size=theme_params.get("min_room_size", self.min_room_size),
                max_room_size=theme_params.get("max_room_size", self.max_room_size),
                room_types=theme_params.get("room_types", self.room_types)
            )
        except Exception as e:
            self.logger.error(f"Error generating themed level: {str(e)}")
            return self.generate_level(num_rooms)
    
    def _get_theme_parameters(self, theme: str) -> Dict[str, Any]:
        """Get level generation parameters for a theme using MCP"""
        prompt = f"""
        Generate parameters for a procedural level with the theme: {theme}
        
        Return a JSON object with the following structure:
        {{
            "min_room_size": float,
            "max_room_size": float,
            "room_types": {{
                "type1": probability,
                "type2": probability,
                ...
            }}
        }}
        
        The probabilities should sum to 1.0.
        Room types should be one of: default, treasure, enemy, boss, shop, or create new appropriate types.
        """
        
        try:
            # Call MCP to generate parameters
            response = self.mcp_client.execute_tool("generate_json", {"prompt": prompt})
            
            if "error" in response:
                self.logger.warning(f"Error from MCP: {response['error']}")
                return {}
            
            # Parse and validate parameters
            params = response.get("json", {})
            
            # Validate room types probabilities
            room_types = params.get("room_types", {})
            if room_types:
                total_prob = sum(room_types.values())
                if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors
                    # Normalize probabilities
                    for room_type in room_types:
                        room_types[room_type] /= total_prob
            
            return params
        except Exception as e:
            self.logger.error(f"Error getting theme parameters: {str(e)}")
            return {}
    
    def generate_story_based_level(self, story_context: str, num_rooms: int = 10) -> Tuple[List[Room], List[Corridor]]:
        """Generate a level based on a story context using MCP"""
        if not self.mcp_client:
            self.logger.warning("No MCP client provided, falling back to standard generation")
            return self.generate_level(num_rooms)
        
        try:
            # Get level structure from MCP based on story
            level_structure = self._get_story_level_structure(story_context, num_rooms)
            
            # Clear existing data
            self.rooms = []
            self.corridors = []
            
            # Create rooms based on structure
            for room_data in level_structure.get("rooms", []):
                position = Vector3(
                    room_data.get("x", 0),
                    room_data.get("y", 0),
                    room_data.get("z", 0)
                )
                
                width = room_data.get("width", random.uniform(self.min_room_size, self.max_room_size))
                height = room_data.get("height", random.uniform(self.min_room_size/2, self.max_room_size/2))
                depth = room_data.get("depth", random.uniform(self.min_room_size, self.max_room_size))
                
                room_type = room_data.get("type", "default")
                
                room = Room(position, width, height, depth, room_type)
                self.rooms.append(room)
            
            # Connect rooms
            self._connect_rooms()
            
            return self.rooms, self.corridors
        except Exception as e:
            self.logger.error(f"Error generating story-based level: {str(e)}")
            return self.generate_level(num_rooms)
    
    def _get_story_level_structure(self, story_context: str, num_rooms: int) -> Dict[str, Any]:
        """Get level structure based on a story context using MCP"""
        prompt = f"""
        Generate a level structure based on this story context:
        {story_context}
        
        The level should have approximately {num_rooms} rooms.
        
        Return a JSON object with the following structure:
        {{
            "rooms": [
                {{
                    "x": float,
                    "y": float,
                    "z": float,
                    "width": float,
                    "height": float,
                    "depth": float,
                    "type": string,
                    "description": string
                }},
                ...
            ]
        }}
        
        Room types should be one of: default, treasure, enemy, boss, shop, or create new appropriate types.
        Position coordinates should be between -50 and 50.
        Room sizes should be between 5 and 15.
        """
        
        try:
            # Call MCP to generate level structure
            response = self.mcp_client.execute_tool("generate_json", {"prompt": prompt})
            
            if "error" in response:
                self.logger.warning(f"Error from MCP: {response['error']}")
                return {"rooms": []}
            
            # Parse and validate structure
            structure = response.get("json", {"rooms": []})
            
            # Ensure we have rooms
            if not structure.get("rooms"):
                self.logger.warning("No rooms in generated structure")
                return {"rooms": []}
            
            return structure
        except Exception as e:
            self.logger.error(f"Error getting story level structure: {str(e)}")
            return {"rooms": []}