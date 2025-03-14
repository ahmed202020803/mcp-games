"""
Advanced Game Engine with Integrated Systems
"""

import time
import logging
import pygame
from typing import Dict, List, Any, Optional, Tuple, Set, Callable

from .game_engine import GameObject, Player, NPC
from .physics import PhysicsSystem, SphereCollider, BoxCollider, Vector3
from .renderer import RenderSystem, RenderComponent, Camera, ParticleSystem

class InputSystem:
    """System for handling user input"""
    
    def __init__(self):
        self.key_states = {}  # Current state of keys
        self.prev_key_states = {}  # Previous state of keys
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.prev_mouse_buttons = [False, False, False]
        self.key_bindings: Dict[int, str] = {}  # Maps key codes to action names
        self.action_handlers: Dict[str, Callable] = {}  # Maps action names to handler functions
    
    def bind_key(self, key_code: int, action_name: str):
        """Bind a key to an action"""
        self.key_bindings[key_code] = action_name
    
    def register_action_handler(self, action_name: str, handler: Callable):
        """Register a handler function for an action"""
        self.action_handlers[action_name] = handler
    
    def update(self):
        """Update input state"""
        # Store previous states
        self.prev_key_states = self.key_states.copy()
        self.prev_mouse_buttons = self.mouse_buttons.copy()
        
        # Get current keyboard state
        keys = pygame.key.get_pressed()
        for key_code in self.key_bindings:
            self.key_states[key_code] = keys[key_code]
        
        # Get current mouse state
        self.mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed(3)  # Get all 3 mouse buttons
        self.mouse_buttons = list(mouse_buttons)
        
        # Process actions
        for key_code, action_name in self.key_bindings.items():
            # Key just pressed
            if self.key_states.get(key_code, False) and not self.prev_key_states.get(key_code, False):
                if action_name in self.action_handlers:
                    self.action_handlers[action_name](True)
            
            # Key just released
            elif not self.key_states.get(key_code, False) and self.prev_key_states.get(key_code, False):
                if action_name in self.action_handlers:
                    self.action_handlers[action_name](False)
    
    def is_key_pressed(self, key_code: int) -> bool:
        """Check if a key is currently pressed"""
        return self.key_states.get(key_code, False)
    
    def is_key_just_pressed(self, key_code: int) -> bool:
        """Check if a key was just pressed this frame"""
        return self.key_states.get(key_code, False) and not self.prev_key_states.get(key_code, False)
    
    def is_key_just_released(self, key_code: int) -> bool:
        """Check if a key was just released this frame"""
        return not self.key_states.get(key_code, False) and self.prev_key_states.get(key_code, False)
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed"""
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed this frame"""
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button] and not self.prev_mouse_buttons[button]
        return False
    
    def is_mouse_button_just_released(self, button: int) -> bool:
        """Check if a mouse button was just released this frame"""
        if 0 <= button < len(self.mouse_buttons):
            return not self.mouse_buttons[button] and self.prev_mouse_buttons[button]
        return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position"""
        return self.mouse_pos


class SoundSystem:
    """System for audio playback"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_track: Optional[str] = None
        self.volume = 1.0
        self.music_volume = 1.0
        self.enabled = True
        self.logger = logging.getLogger("mcp_games.engine.sound")
    
    def load_sound(self, name: str, file_path: str) -> bool:
        """Load a sound effect"""
        try:
            self.sounds[name] = pygame.mixer.Sound(file_path)
            return True
        except pygame.error as e:
            self.logger.error(f"Failed to load sound '{name}' from {file_path}: {str(e)}")
            return False
    
    def play_sound(self, name: str, volume: float = 1.0, loops: int = 0) -> bool:
        """Play a sound effect"""
        if not self.enabled:
            return False
            
        if name in self.sounds:
            # Set volume for this sound (adjusted by master volume)
            self.sounds[name].set_volume(volume * self.volume)
            
            # Play the sound
            self.sounds[name].play(loops)
            return True
        else:
            self.logger.warning(f"Sound '{name}' not found")
            return False
    
    def stop_sound(self, name: str) -> bool:
        """Stop a sound effect"""
        if name in self.sounds:
            self.sounds[name].stop()
            return True
        else:
            self.logger.warning(f"Sound '{name}' not found")
            return False
    
    def play_music(self, file_path: str, loops: int = -1, fade_ms: int = 0) -> bool:
        """Play background music"""
        if not self.enabled:
            return False
            
        try:
            # Stop current music if playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            
            # Load and play new music
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.music_volume)
            
            if fade_ms > 0:
                pygame.mixer.music.play(loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops)
                
            self.music_track = file_path
            return True
        except pygame.error as e:
            self.logger.error(f"Failed to play music from {file_path}: {str(e)}")
            return False
    
    def stop_music(self, fade_ms: int = 0) -> bool:
        """Stop background music"""
        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            
            self.music_track = None
            return True
        except pygame.error as e:
            self.logger.error(f"Failed to stop music: {str(e)}")
            return False
    
    def set_volume(self, volume: float):
        """Set master volume for sound effects"""
        self.volume = max(0.0, min(1.0, volume))
        
        # Update volume for all loaded sounds
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def set_music_volume(self, volume: float):
        """Set volume for background music"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_enabled(self):
        """Toggle sound on/off"""
        self.enabled = not self.enabled
        
        if not self.enabled:
            # Stop all sounds and music
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        elif self.music_track:
            # Restart music if we have a track
            self.play_music(self.music_track)


class AdvancedGameEngine:
    """Advanced game engine with integrated systems"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, title: str = "MCP Advanced Game"):
        # Initialize pygame
        pygame.init()
        
        # Core engine components
        self.objects: Dict[str, GameObject] = {}
        self.running = False
        self.paused = False
        self.last_update_time = 0
        self.delta_time = 0
        self.frame_count = 0
        self.fps = 60
        self.target_fps = 60
        self.logger = logging.getLogger("mcp_games.engine.advanced")
        
        # Integrated systems
        self.physics_system = PhysicsSystem()
        self.render_system = RenderSystem(screen_width, screen_height, title)
        self.input_system = InputSystem()
        self.sound_system = SoundSystem()
        
        # Scene management
        self.current_scene: Optional[str] = None
        self.scenes: Dict[str, Dict[str, GameObject]] = {}
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Setup default input bindings
        self._setup_default_input_bindings()
        
        # Clock for frame timing
        self.clock = pygame.time.Clock()
    
    def _setup_default_input_bindings(self):
        """Setup default input bindings"""
        # Bind escape key to quit
        self.input_system.bind_key(pygame.K_ESCAPE, "quit")
        self.input_system.register_action_handler("quit", lambda pressed: self.stop() if pressed else None)
        
        # Bind P key to toggle pause
        self.input_system.bind_key(pygame.K_p, "toggle_pause")
        self.input_system.register_action_handler("toggle_pause", 
                                                 lambda pressed: self.toggle_pause() if pressed else None)
        
        # Bind F1 key to toggle debug mode
        self.input_system.bind_key(pygame.K_F1, "toggle_debug")
        self.input_system.register_action_handler("toggle_debug", 
                                                 lambda pressed: self.render_system.toggle_debug_mode() if pressed else None)
    
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
    
    def add_object(self, game_object: GameObject):
        """Add an existing game object to the engine"""
        self.objects[game_object.id] = game_object
    
    def remove_object(self, object_id: str) -> bool:
        """Remove a game object from the engine"""
        if object_id in self.objects:
            del self.objects[object_id]
            return True
        return False
    
    def add_collider(self, game_object: GameObject, collider_type: str = "sphere", **kwargs):
        """Add a collider to a game object"""
        if collider_type.lower() == "sphere":
            radius = kwargs.get("radius", 1.0)
            collider = SphereCollider(game_object, radius)
        elif collider_type.lower() == "box":
            size = kwargs.get("size", Vector3(1.0, 1.0, 1.0))
            collider = BoxCollider(game_object, size)
        else:
            self.logger.warning(f"Unknown collider type: {collider_type}")
            return None
        
        # Set collider properties
        collider.is_trigger = kwargs.get("is_trigger", False)
        collider.layer = kwargs.get("layer", 0)
        
        # Add to physics system
        self.physics_system.add_collider(collider)
        
        # Store reference on game object
        game_object.set_property("collider", collider)
        
        return collider
    
    def add_render_component(self, game_object: GameObject, sprite_path: Optional[str] = None):
        """Add a render component to a game object"""
        render_component = RenderComponent(game_object, sprite_path)
        self.render_system.add_render_component(render_component)
        
        # Store reference on game object
        game_object.set_property("render_component", render_component)
        
        return render_component
    
    def create_particle_system(self, position: Vector3) -> ParticleSystem:
        """Create a particle system"""
        particle_system = ParticleSystem(position)
        self.render_system.add_particle_system(particle_system)
        return particle_system
    
    def register_event_handler(self, event_name: str, handler: Callable):
        """Register a handler for an event"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
    
    def trigger_event(self, event_name: str, **kwargs):
        """Trigger an event"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                handler(**kwargs)
    
    def create_scene(self, scene_name: str) -> bool:
        """Create a new scene"""
        if scene_name in self.scenes:
            self.logger.warning(f"Scene '{scene_name}' already exists")
            return False
        
        self.scenes[scene_name] = {}
        return True
    
    def load_scene(self, scene_name: str) -> bool:
        """Load a scene"""
        if scene_name not in self.scenes:
            self.logger.warning(f"Scene '{scene_name}' not found")
            return False
        
        # Clear current objects
        self.objects = {}
        
        # Load objects from scene
        self.objects = self.scenes[scene_name].copy()
        
        # Set current scene
        self.current_scene = scene_name
        
        # Trigger scene loaded event
        self.trigger_event("scene_loaded", scene_name=scene_name)
        
        return True
    
    def save_scene(self, scene_name: Optional[str] = None) -> bool:
        """Save current objects to a scene"""
        if scene_name is None:
            scene_name = self.current_scene
        
        if scene_name is None:
            self.logger.warning("No scene name specified and no current scene")
            return False
        
        # Save current objects to scene
        self.scenes[scene_name] = self.objects.copy()
        
        # Trigger scene saved event
        self.trigger_event("scene_saved", scene_name=scene_name)
        
        return True
    
    def update(self, delta_time: float):
        """Update all game systems and objects"""
        if self.paused:
            return
        
        # Process pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
        
        # Update input system
        self.input_system.update()
        
        # Update physics
        self.physics_system.update(delta_time)
        
        # Update game objects
        for obj in self.objects.values():
            obj.update(delta_time)
        
        # Trigger update event
        self.trigger_event("update", delta_time=delta_time)
    
    def render(self):
        """Render the current frame"""
        # Use the render system to render everything
        self.render_system.render()
        
        # Trigger render event
        self.trigger_event("render")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        self.logger.info(f"Game {'paused' if self.paused else 'resumed'}")
        
        # Trigger pause event
        self.trigger_event("pause_toggled", paused=self.paused)
    
    def start(self):
        """Start the game loop"""
        self.running = True
        self.last_update_time = time.time()
        
        self.logger.info("Advanced game engine started")
        
        try:
            while self.running:
                # Calculate delta time
                current_time = time.time()
                self.delta_time = current_time - self.last_update_time
                self.last_update_time = current_time
                
                # Update game state
                self.update(self.delta_time)
                
                # Render
                self.render()
                
                # Increment frame counter
                self.frame_count += 1
                
                # Calculate FPS
                if self.frame_count % 60 == 0:
                    self.fps = int(1.0 / max(0.001, self.delta_time))
                
                # Cap frame rate
                self.clock.tick(self.target_fps)
                
        except KeyboardInterrupt:
            self.logger.info("Game engine stopped by user")
        except Exception as e:
            self.logger.error(f"Error in game loop: {str(e)}", exc_info=True)
        finally:
            self.running = False
            pygame.quit()
            self.logger.info("Advanced game engine stopped")
    
    def stop(self):
        """Stop the game loop"""
        self.running = False
        
        # Trigger stop event
        self.trigger_event("engine_stopped")