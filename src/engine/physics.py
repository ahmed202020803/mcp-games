"""
Physics System for MCP Games
"""

import math
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass

@dataclass
class Vector3:
    """3D Vector class"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar):
        if scalar == 0:
            return Vector3()
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return self / mag
        return Vector3()
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def distance_to(self, other) -> float:
        return (self - other).magnitude()
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    @staticmethod
    def from_tuple(t: Tuple[float, float, float]):
        return Vector3(t[0], t[1], t[2])


class Collider:
    """Base class for all colliders"""
    
    def __init__(self, game_object: Any):
        self.game_object = game_object
        self.position = Vector3.from_tuple(game_object.position)
        self.is_trigger = False
        self.layer = 0
    
    def update_position(self):
        """Update collider position based on game object"""
        self.position = Vector3.from_tuple(self.game_object.position)
    
    def intersects(self, other: 'Collider') -> bool:
        """Check if this collider intersects with another"""
        return False


class SphereCollider(Collider):
    """Spherical collision volume"""
    
    def __init__(self, game_object: Any, radius: float = 1.0):
        super().__init__(game_object)
        self.radius = radius
    
    def intersects(self, other: Collider) -> bool:
        """Check if this sphere collider intersects with another collider"""
        if isinstance(other, SphereCollider):
            # Sphere-Sphere collision
            distance = self.position.distance_to(other.position)
            return distance < (self.radius + other.radius)
        elif isinstance(other, BoxCollider):
            # Sphere-Box collision (simplified)
            closest_point = Vector3(
                max(other.min.x, min(self.position.x, other.max.x)),
                max(other.min.y, min(self.position.y, other.max.y)),
                max(other.min.z, min(self.position.z, other.max.z))
            )
            distance = self.position.distance_to(closest_point)
            return distance < self.radius
        return False


class BoxCollider(Collider):
    """Box-shaped collision volume"""
    
    def __init__(self, game_object: Any, size: Vector3 = Vector3(1.0, 1.0, 1.0)):
        super().__init__(game_object)
        self.size = size
        self.update_bounds()
    
    def update_position(self):
        """Update collider position and bounds"""
        super().update_position()
        self.update_bounds()
    
    def update_bounds(self):
        """Update min and max bounds based on position and size"""
        half_size = self.size * 0.5
        self.min = self.position - half_size
        self.max = self.position + half_size
    
    def intersects(self, other: Collider) -> bool:
        """Check if this box collider intersects with another collider"""
        if isinstance(other, BoxCollider):
            # Box-Box collision
            return (
                self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z
            )
        elif isinstance(other, SphereCollider):
            # Box-Sphere collision (call the sphere's method)
            return other.intersects(self)
        return False


class PhysicsSystem:
    """Physics system for collision detection and resolution"""
    
    def __init__(self):
        self.colliders: List[Collider] = []
        self.collision_matrix: Dict[int, Set[int]] = {}  # Layer-based collision filtering
        self.gravity = Vector3(0, -9.81, 0)
        self.collision_callbacks: Dict[Any, callable] = {}
    
    def add_collider(self, collider: Collider):
        """Add a collider to the physics system"""
        self.colliders.append(collider)
    
    def remove_collider(self, collider: Collider):
        """Remove a collider from the physics system"""
        if collider in self.colliders:
            self.colliders.remove(collider)
    
    def set_layer_collision(self, layer1: int, layer2: int, should_collide: bool):
        """Set whether two layers should collide with each other"""
        if layer1 not in self.collision_matrix:
            self.collision_matrix[layer1] = set()
        
        if should_collide:
            self.collision_matrix[layer1].add(layer2)
        elif layer2 in self.collision_matrix[layer1]:
            self.collision_matrix[layer1].remove(layer2)
    
    def should_check_collision(self, layer1: int, layer2: int) -> bool:
        """Check if two layers should collide based on the collision matrix"""
        return (
            (layer1 in self.collision_matrix and layer2 in self.collision_matrix[layer1]) or
            (layer2 in self.collision_matrix and layer1 in self.collision_matrix[layer2])
        )
    
    def register_collision_callback(self, game_object: Any, callback: callable):
        """Register a callback function for collision events"""
        self.collision_callbacks[game_object] = callback
    
    def update(self, delta_time: float):
        """Update physics and detect collisions"""
        # Update collider positions
        for collider in self.colliders:
            collider.update_position()
        
        # Check for collisions
        collisions = []
        for i, collider1 in enumerate(self.colliders):
            for collider2 in self.colliders[i+1:]:
                # Skip if layers shouldn't collide
                if not self.should_check_collision(collider1.layer, collider2.layer):
                    continue
                
                if collider1.intersects(collider2):
                    collisions.append((collider1, collider2))
        
        # Handle collisions
        for collider1, collider2 in collisions:
            # Trigger callbacks if registered
            if collider1.game_object in self.collision_callbacks:
                self.collision_callbacks[collider1.game_object](collider1.game_object, collider2.game_object)
            
            if collider2.game_object in self.collision_callbacks:
                self.collision_callbacks[collider2.game_object](collider2.game_object, collider1.game_object)
            
            # If either is a trigger, don't resolve physically
            if collider1.is_trigger or collider2.is_trigger:
                continue
            
            # Simple collision resolution (push objects apart)
            self._resolve_collision(collider1, collider2)
    
    def _resolve_collision(self, collider1: Collider, collider2: Collider):
        """Simple collision resolution"""
        # Only handle sphere-sphere for simplicity in this example
        if isinstance(collider1, SphereCollider) and isinstance(collider2, SphereCollider):
            direction = Vector3.from_tuple(collider1.game_object.position) - Vector3.from_tuple(collider2.game_object.position)
            distance = direction.magnitude()
            
            if distance == 0:
                # If objects are at the same position, push in a random direction
                direction = Vector3(1, 0, 0)
                distance = 1
            
            overlap = (collider1.radius + collider2.radius) - distance
            
            if overlap > 0:
                # Push objects apart
                direction = direction.normalize()
                push_vector = direction * (overlap * 0.5)
                
                # Update positions
                pos1 = Vector3.from_tuple(collider1.game_object.position) + push_vector
                pos2 = Vector3.from_tuple(collider2.game_object.position) - push_vector
                
                collider1.game_object.position = pos1.to_tuple()
                collider2.game_object.position = pos2.to_tuple()