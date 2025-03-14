"""
Behavior System for AI-driven Game Objects
"""

from typing import Dict, List, Any, Callable, Optional
from abc import ABC, abstractmethod

class Behavior(ABC):
    """Abstract base class for all behaviors"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def update(self, game_object: Any, delta_time: float):
        """Update the behavior"""
        pass


class CompositeBehavior(Behavior):
    """Behavior composed of multiple sub-behaviors"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.behaviors: List[Behavior] = []
        
    def add_behavior(self, behavior: Behavior):
        """Add a sub-behavior"""
        self.behaviors.append(behavior)
        
    def update(self, game_object: Any, delta_time: float):
        """Update all sub-behaviors"""
        for behavior in self.behaviors:
            behavior.update(game_object, delta_time)


class StateMachineBehavior(Behavior):
    """Behavior based on a finite state machine"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.states: Dict[str, Callable[[Any, float], None]] = {}
        self.transitions: Dict[str, Dict[str, Callable[[Any], bool]]] = {}
        self.current_state: Optional[str] = None
        
    def add_state(self, state_name: str, update_func: Callable[[Any, float], None]):
        """Add a state to the state machine"""
        self.states[state_name] = update_func
        self.transitions[state_name] = {}
        
    def add_transition(self, from_state: str, to_state: str, condition: Callable[[Any], bool]):
        """Add a transition between states"""
        if from_state in self.transitions:
            self.transitions[from_state][to_state] = condition
        
    def set_initial_state(self, state_name: str):
        """Set the initial state"""
        if state_name in self.states:
            self.current_state = state_name
        
    def update(self, game_object: Any, delta_time: float):
        """Update the current state and check for transitions"""
        if not self.current_state:
            return
            
        # Check for transitions
        if self.current_state in self.transitions:
            for to_state, condition in self.transitions[self.current_state].items():
                if condition(game_object):
                    self.current_state = to_state
                    break
                    
        # Update current state
        if self.current_state in self.states:
            self.states[self.current_state](game_object, delta_time)


class WanderBehavior(Behavior):
    """Simple wandering behavior"""
    
    def __init__(self, name: str = "wander", speed: float = 1.0, radius: float = 10.0):
        super().__init__(name)
        self.speed = speed
        self.radius = radius
        self.target_position = None
        self.time_to_new_target = 0
        
    def update(self, game_object: Any, delta_time: float):
        """Update wandering behavior"""
        import random
        
        # Generate new target position if needed
        self.time_to_new_target -= delta_time
        if self.time_to_new_target <= 0 or not self.target_position:
            x, y, z = game_object.position
            self.target_position = (
                x + random.uniform(-self.radius, self.radius),
                y,
                z + random.uniform(-self.radius, self.radius)
            )
            self.time_to_new_target = random.uniform(2.0, 5.0)
            
        # Move towards target position
        if self.target_position:
            tx, ty, tz = self.target_position
            x, y, z = game_object.position
            
            # Calculate direction vector
            dx = tx - x
            dz = tz - z
            
            # Normalize
            length = (dx**2 + dz**2)**0.5
            if length > 0.1:
                dx /= length
                dz /= length
                
                # Move
                game_object.position = (
                    x + dx * self.speed * delta_time,
                    y,
                    z + dz * self.speed * delta_time
                )


class FollowBehavior(Behavior):
    """Behavior to follow another game object"""
    
    def __init__(self, name: str = "follow", target_id: str = "", min_distance: float = 2.0, speed: float = 1.5):
        super().__init__(name)
        self.target_id = target_id
        self.min_distance = min_distance
        self.speed = speed
        
    def update(self, game_object: Any, delta_time: float):
        """Update following behavior"""
        # Get target from game engine
        if hasattr(game_object, 'get_property'):
            engine = game_object.get_property('engine')
            if engine:
                target = engine.get_object(self.target_id)
                if target:
                    # Calculate distance
                    tx, ty, tz = target.position
                    x, y, z = game_object.position
                    
                    dx = tx - x
                    dz = tz - z
                    
                    distance = (dx**2 + dz**2)**0.5
                    
                    # Move if too far
                    if distance > self.min_distance:
                        # Normalize
                        dx /= distance
                        dz /= distance
                        
                        # Move
                        game_object.position = (
                            x + dx * self.speed * delta_time,
                            y,
                            z + dz * self.speed * delta_time
                        )