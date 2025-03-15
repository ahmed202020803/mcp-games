"""
Advanced Game Engine for MCP Games
"""

import os
import sys
import time
import logging
import pygame
import random
from typing import Dict, List, Any, Optional, Tuple, Callable, Set, Union
from enum import Enum, auto

from .physics import PhysicsSystem, Vector3, BoxCollider, SphereCollider
from .renderer import RenderSystem, Sprite, ParticleSystem, Camera
from .weather import WeatherSystem, WeatherType

# Input System
class InputSystem:
    """Handles user input and key bindings"""
    
    def __init__(self):
        self.key_bindings: Dict[int, str] = {}  # Maps pygame key constants to action names
        self.action_handlers: Dict[str, List[Callable[[], None]]] = {}  # Maps action names to handler functions
        self.keys_pressed: Set[int] = set()  # Currently pressed keys
        self.keys_just_pressed: Set[int] = set()  # Keys pressed this frame
        self.keys_just_released: Set[int] = set()  # Keys released this frame
        self.mouse_position: Tuple[int, int] = (0, 0)  # Current mouse position
        self.mouse_buttons: Dict[int, bool] = {1: False, 2: False, 3: False}  # Mouse button states
        self.mouse_buttons_just_pressed: Set[int] = set()  # Mouse buttons pressed this frame
        self.mouse_buttons_just_released: Set[int] = set()  # Mouse buttons released this frame
        self.logger = logging.getLogger("mcp_games.engine.input")
    
    def bind_key(self, key: int, action: str):
        """Bind a key to an action"""
        self.key_bindings[key] = action
        self.logger.debug(f"Bound key {pygame.key.name(key)} to action '{action}'")
    
    def register_action_handler(self, action: str, handler: Callable[[], None]):
        """Register a handler function for an action"""
        if action not in self.action_handlers:
            self.action_handlers[action] = []
        self.action_handlers[action].append(handler)
        self.logger.debug(f"Registered handler for action '{action}'")
    
    def process_events(self, events: List[pygame.event.Event]):
        """Process pygame events"""
        # Clear just pressed/released sets
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
        
        # Process events
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
                
                # Trigger action if key is bound
                if event.key in self.key_bindings:
                    action = self.key_bindings[event.key]
                    self._trigger_action(action)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)
                self.keys_just_released.add(event.key)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_position = event.pos
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[event.button] = True
                self.mouse_buttons_just_pressed.add(event.button)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button] = False
                self.mouse_buttons_just_released.add(event.button)
    
    def _trigger_action(self, action: str):
        """Trigger all handlers for an action"""
        if action in self.action_handlers:
            for handler in self.action_handlers[action]:
                handler()
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if a key was just pressed this frame"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """Check if a key was just released this frame"""
        return key in self.keys_just_released
    
    def is_action_pressed(self, action: str) -> bool:
        """Check if any key bound to an action is pressed"""
        for key, bound_action in self.key_bindings.items():
            if bound_action == action and key in self.keys_pressed:
                return True
        return False
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed"""
        return self.mouse_buttons.get(button, False)
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame"""
        return button in self.mouse_buttons_just_pressed
    
    def is_mouse_button_just_released(self, button: int) -> bool:
        """Check if a mouse button was just released this frame"""
        return button in self.mouse_buttons_just_released
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position"""
        return self.mouse_position


# Sound System
class SoundSystem:
    """Handles audio playback and sound effects"""
    
    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}  # Maps track names to file paths
        self.current_music_track: Optional[str] = None
        self.sound_volume = 1.0  # 0.0 to 1.0
        self.music_volume = 1.0  # 0.0 to 1.0
        self.logger = logging.getLogger("mcp_games.engine.sound")
        
        # Initialize pygame mixer
        pygame.mixer.init()
    
    def load_sound(self, name: str, file_path: str):
        """Load a sound effect"""
        try:
            sound = pygame.mixer.Sound(file_path)
            self.sounds[name] = sound
            self.logger.debug(f"Loaded sound '{name}' from {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to load sound '{name}' from {file_path}: {e}")
    
    def load_music(self, name: str, file_path: str):
        """Register a music track"""
        self.music_tracks[name] = file_path
        self.logger.debug(f"Registered music track '{name}' from {file_path}")
    
    def play_sound(self, name: str, volume: float = None, loops: int = 0):
        """Play a sound effect"""
        if name in self.sounds:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume * self.sound_volume)
            else:
                sound.set_volume(self.sound_volume)
            sound.play(loops=loops)
            self.logger.debug(f"Playing sound '{name}'")
        else:
            self.logger.warning(f"Sound '{name}' not found")
    
    def play_music(self, name: str, loops: int = -1, fade_ms: int = 500):
        """Play a music track"""
        if name in self.music_tracks:
            file_path = self.music_tracks[name]
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                self.current_music_track = name
                self.logger.debug(f"Playing music track '{name}'")
            except Exception as e:
                self.logger.error(f"Failed to play music track '{name}': {e}")
        else:
            self.logger.warning(f"Music track '{name}' not found")
    
    def stop_music(self, fade_ms: int = 500):
        """Stop the current music track"""
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music_track = None
        self.logger.debug("Stopped music")
    
    def pause_music(self):
        """Pause the current music track"""
        pygame.mixer.music.pause()
        self.logger.debug("Paused music")
    
    def unpause_music(self):
        """Unpause the current music track"""
        pygame.mixer.music.unpause()
        self.logger.debug("Unpaused music")
    
    def set_sound_volume(self, volume: float):
        """Set the volume for sound effects"""
        self.sound_volume = max(0.0, min(1.0, volume))
        self.logger.debug(f"Set sound volume to {self.sound_volume}")
    
    def set_music_volume(self, volume: float):
        """Set the volume for music"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        self.logger.debug(f"Set music volume to {self.music_volume}")


# Scene Management
class Scene:
    """Represents a game scene or level"""
    
    def __init__(self, name: str):
        self.name = name
        self.game_objects: List[Any] = []
        self.active = False
        self.logger = logging.getLogger(f"mcp_games.engine.scene.{name}")
    
    def add_game_object(self, game_object: Any):
        """Add a game object to the scene"""
        self.game_objects.append(game_object)
        game_object.scene = self
        self.logger.debug(f"Added game object {game_object.name} to scene {self.name}")
    
    def remove_game_object(self, game_object: Any):
        """Remove a game object from the scene"""
        if game_object in self.game_objects:
            self.game_objects.remove(game_object)
            game_object.scene = None
            self.logger.debug(f"Removed game object {game_object.name} from scene {self.name}")
    
    def get_game_objects_by_tag(self, tag: str) -> List[Any]:
        """Get all game objects with a specific tag"""
        return [obj for obj in self.game_objects if hasattr(obj, 'tag') and obj.tag == tag]
    
    def get_game_object_by_name(self, name: str) -> Optional[Any]:
        """Get a game object by name"""
        for obj in self.game_objects:
            if hasattr(obj, 'name') and obj.name == name:
                return obj
        return None
    
    def update(self, delta_time: float):
        """Update all game objects in the scene"""
        for game_object in self.game_objects:
            if hasattr(game_object, 'update'):
                game_object.update(delta_time)
    
    def render(self, render_system: Any):
        """Render all game objects in the scene"""
        for game_object in self.game_objects:
            if hasattr(game_object, 'render'):
                game_object.render(render_system)
    
    def on_activate(self):
        """Called when the scene becomes active"""
        self.active = True
        self.logger.info(f"Scene {self.name} activated")
        
        # Activate all game objects
        for game_object in self.game_objects:
            if hasattr(game_object, 'on_activate'):
                game_object.on_activate()
    
    def on_deactivate(self):
        """Called when the scene becomes inactive"""
        self.active = False
        self.logger.info(f"Scene {self.name} deactivated")
        
        # Deactivate all game objects
        for game_object in self.game_objects:
            if hasattr(game_object, 'on_deactivate'):
                game_object.on_deactivate()


# Event System
class EventSystem:
    """Handles game events and callbacks"""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable[..., None]]] = {}
        self.scheduled_events: List[Tuple[float, str, List[Any], Dict[str, Any]]] = []
        self.logger = logging.getLogger("mcp_games.engine.events")
    
    def register_event_handler(self, event_name: str, handler: Callable[..., None]):
        """Register a handler for an event"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
        self.logger.debug(f"Registered handler for event '{event_name}'")
    
    def unregister_event_handler(self, event_name: str, handler: Callable[..., None]):
        """Unregister a handler for an event"""
        if event_name in self.event_handlers and handler in self.event_handlers[event_name]:
            self.event_handlers[event_name].remove(handler)
            self.logger.debug(f"Unregistered handler for event '{event_name}'")
    
    def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger an event with arguments"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in event handler for '{event_name}': {e}")
            self.logger.debug(f"Triggered event '{event_name}'")
    
    def schedule_event(self, delay: float, event_name: str, *args, **kwargs):
        """Schedule an event to be triggered after a delay (in seconds)"""
        self.scheduled_events.append((time.time() + delay, event_name, args, kwargs))
        self.logger.debug(f"Scheduled event '{event_name}' with {delay}s delay")
    
    def update(self):
        """Update scheduled events"""
        current_time = time.time()
        triggered_events = []
        
        # Find events to trigger
        for event in self.scheduled_events:
            trigger_time, event_name, args, kwargs = event
            if current_time >= trigger_time:
                self.trigger_event(event_name, *args, **kwargs)
                triggered_events.append(event)
        
        # Remove triggered events
        for event in triggered_events:
            self.scheduled_events.remove(event)


# Game Object
class GameObject:
    """Base class for all game objects"""
    
    def __init__(self, name: str, position: Tuple[float, float, float] = (0, 0, 0)):
        self.name = name
        self.position = position
        self.rotation = (0, 0, 0)  # Euler angles (x, y, z) in degrees
        self.scale = (1, 1, 1)
        self.tag = ""
        self.active = True
        self.scene = None
        self.properties: Dict[str, Any] = {}
        self.components: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"mcp_games.engine.gameobject.{name}")
    
    def update(self, delta_time: float):
        """Update the game object"""
        # Update components
        for component_name, component in self.components.items():
            if hasattr(component, 'update'):
                component.update(delta_time)
    
    def render(self, render_system: Any):
        """Render the game object"""
        # Render components
        for component_name, component in self.components.items():
            if hasattr(component, 'render'):
                component.render(render_system)
    
    def add_component(self, name: str, component: Any):
        """Add a component to the game object"""
        self.components[name] = component
        if hasattr(component, 'game_object'):
            component.game_object = self
        self.logger.debug(f"Added component '{name}' to {self.name}")
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name"""
        return self.components.get(name)
    
    def remove_component(self, name: str):
        """Remove a component by name"""
        if name in self.components:
            component = self.components[name]
            if hasattr(component, 'game_object'):
                component.game_object = None
            del self.components[name]
            self.logger.debug(f"Removed component '{name}' from {self.name}")
    
    def set_property(self, name: str, value: Any):
        """Set a property value"""
        self.properties[name] = value
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """Get a property value"""
        return self.properties.get(name, default)
    
    def on_activate(self):
        """Called when the game object becomes active"""
        self.active = True
        
        # Activate components
        for component_name, component in self.components.items():
            if hasattr(component, 'on_activate'):
                component.on_activate()
    
    def on_deactivate(self):
        """Called when the game object becomes inactive"""
        self.active = False
        
        # Deactivate components
        for component_name, component in self.components.items():
            if hasattr(component, 'on_deactivate'):
                component.on_deactivate()
    
    def on_collision(self, other: 'GameObject', contact_point: Vector3):
        """Called when this object collides with another"""
        # Notify components
        for component_name, component in self.components.items():
            if hasattr(component, 'on_collision'):
                component.on_collision(other, contact_point)


# Advanced Game Engine
class AdvancedGameEngine:
    """Advanced game engine with physics, rendering, and AI integration"""
    
    def __init__(self, title: str = "MCP Game", width: int = 800, height: int = 600):
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("mcp_games.engine")
        
        # Initialize pygame
        pygame.init()
        
        # Create window
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        # Create systems
        self.physics_system = PhysicsSystem()
        self.render_system = RenderSystem(self.screen)
        self.input_system = InputSystem()
        self.sound_system = SoundSystem()
        self.event_system = EventSystem()
        self.weather_system = WeatherSystem(self)
        
        # Scene management
        self.scenes: Dict[str, Scene] = {}
        self.active_scene: Optional[Scene] = None
        
        # Game state
        self.running = False
        self.paused = False
        self.target_fps = 60
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        self.frame_count = 0
        self.game_time = 0
        
        # Register default event handlers
        self.input_system.register_action_handler("quit", self.quit)
        self.input_system.register_action_handler("toggle_pause", self.toggle_pause)
        
        # Bind default keys
        self.input_system.bind_key(pygame.K_ESCAPE, "quit")
        self.input_system.bind_key(pygame.K_p, "toggle_pause")
        
        self.logger.info(f"Advanced Game Engine initialized ({width}x{height})")
    
    def create_scene(self, name: str) -> Scene:
        """Create a new scene"""
        scene = Scene(name)
        self.scenes[name] = scene
        self.logger.info(f"Created scene '{name}'")
        return scene
    
    def set_active_scene(self, name: str):
        """Set the active scene"""
        if name in self.scenes:
            # Deactivate current scene
            if self.active_scene:
                self.active_scene.on_deactivate()
            
            # Activate new scene
            self.active_scene = self.scenes[name]
            self.active_scene.on_activate()
            self.logger.info(f"Set active scene to '{name}'")
        else:
            self.logger.error(f"Scene '{name}' not found")
    
    def create_game_object(self, name: str, position: Tuple[float, float, float] = (0, 0, 0)) -> GameObject:
        """Create a new game object"""
        game_object = GameObject(name, position)
        
        # Add to active scene if available
        if self.active_scene:
            self.active_scene.add_game_object(game_object)
        
        return game_object
    
    def create_sprite(self, position: Vector3, image_path: str = None, color: Tuple[int, int, int] = None, 
                     size: Tuple[int, int] = (32, 32)) -> Sprite:
        """Create a sprite for rendering"""
        sprite = self.render_system.create_sprite(position, image_path, color, size)
        return sprite
    
    def create_particle_system(self, position: Vector3) -> ParticleSystem:
        """Create a particle system"""
        particle_system = self.render_system.create_particle_system(position)
        return particle_system
    
    def add_box_collider(self, game_object: GameObject, size: Vector3) -> BoxCollider:
        """Add a box collider to a game object"""
        position = Vector3.from_tuple(game_object.position)
        collider = BoxCollider(position, size)
        collider.game_object = game_object
        
        # Add to physics system
        self.physics_system.add_collider(collider)
        
        # Add as component
        game_object.add_component("collider", collider)
        
        return collider
    
    def add_sphere_collider(self, game_object: GameObject, radius: float) -> SphereCollider:
        """Add a sphere collider to a game object"""
        position = Vector3.from_tuple(game_object.position)
        collider = SphereCollider(position, radius)
        collider.game_object = game_object
        
        # Add to physics system
        self.physics_system.add_collider(collider)
        
        # Add as component
        game_object.add_component("collider", collider)
        
        return collider
    
    def register_event_handler(self, event_name: str, handler: Callable[..., None]):
        """Register a handler for an event"""
        self.event_system.register_event_handler(event_name, handler)
    
    def trigger_event(self, event_name: str, *args, **kwargs):
        """Trigger an event"""
        self.event_system.trigger_event(event_name, *args, **kwargs)
    
    def schedule_event(self, delay: float, event_name: str, *args, **kwargs):
        """Schedule an event to be triggered after a delay"""
        self.event_system.schedule_event(delay, event_name, *args, **kwargs)
    
    def set_weather(self, weather_type: WeatherType, transition_duration: float = 10.0):
        """Set the current weather with optional transition time"""
        self.weather_system.set_weather(weather_type, transition_duration)
        self.logger.info(f"Setting weather to {weather_type.name} with {transition_duration}s transition")
    
    def toggle_auto_weather(self, enabled: bool = True):
        """Enable or disable automatic weather changes"""
        self.weather_system.auto_change = enabled
        self.logger.info(f"Auto weather changes {'enabled' if enabled else 'disabled'}")
    
    def start(self):
        """Start the game loop"""
        if not self.active_scene:
            self.logger.error("No active scene set")
            return
        
        self.running = True
        self.logger.info("Game loop started")
        
        # Main game loop
        while self.running:
            # Calculate delta time
            self.delta_time = self.clock.tick(self.target_fps) / 1000.0
            self.game_time += self.delta_time
            self.frame_count += 1
            
            # Process events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Process input
            self.input_system.process_events(events)
            
            # Update game state if not paused
            if not self.paused:
                # Update event system
                self.event_system.update()
                
                # Update weather system
                self.weather_system.update(self.delta_time)
                
                # Update physics
                self.physics_system.update(self.delta_time)
                
                # Update active scene
                self.active_scene.update(self.delta_time)
                
                # Apply weather effects to game objects
                for game_object in self.active_scene.game_objects:
                    self.weather_system.apply_weather_effects(game_object, self.delta_time)
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Render scene
            self.active_scene.render(self.render_system)
            
            # Update display
            pygame.display.flip()
        
        # Clean up
        pygame.quit()
        self.logger.info("Game loop ended")
    
    def quit(self):
        """Quit the game"""
        self.running = False
        self.logger.info("Quit requested")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.logger.info(f"Game {'paused' if self.paused else 'unpaused'}")
    
    def set_target_fps(self, fps: int):
        """Set the target frames per second"""
        self.target_fps = max(1, fps)
        self.logger.info(f"Set target FPS to {self.target_fps}")
    
    def get_fps(self) -> float:
        """Get the current FPS"""
        return self.clock.get_fps()
    
    def get_game_time(self) -> float:
        """Get the total game time in seconds"""
        return self.game_time
    
    def get_frame_count(self) -> int:
        """Get the total number of frames"""
        return self.frame_count