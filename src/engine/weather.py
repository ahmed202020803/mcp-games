"""
Weather System for MCP Games
"""

import random
import math
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum, auto
from dataclasses import dataclass

from .physics import Vector3
from .renderer import ParticleSystem

class WeatherType(Enum):
    """Types of weather conditions"""
    CLEAR = auto()
    CLOUDY = auto()
    RAIN = auto()
    HEAVY_RAIN = auto()
    STORM = auto()
    SNOW = auto()
    BLIZZARD = auto()
    FOG = auto()
    WINDY = auto()


@dataclass
class WeatherParameters:
    """Parameters for weather conditions"""
    particle_count: int = 0
    particle_size: float = 1.0
    particle_speed: float = 1.0
    particle_color: Tuple[int, int, int] = (255, 255, 255)
    particle_alpha: int = 255
    wind_direction: Vector3 = Vector3(0, 0, 0)
    wind_strength: float = 0.0
    fog_density: float = 0.0
    fog_color: Tuple[int, int, int] = (200, 200, 200)
    lightning_chance: float = 0.0
    sound_effect: Optional[str] = None
    ambient_light: float = 1.0  # 0.0 to 1.0, affects brightness
    visibility_range: float = 100.0  # How far can be seen
    
    @classmethod
    def create_for_weather(cls, weather_type: WeatherType) -> 'WeatherParameters':
        """Create parameters for a specific weather type"""
        if weather_type == WeatherType.CLEAR:
            return cls(
                particle_count=0,
                wind_strength=0.1,
                ambient_light=1.0,
                visibility_range=100.0
            )
        elif weather_type == WeatherType.CLOUDY:
            return cls(
                particle_count=0,
                wind_strength=0.3,
                fog_density=0.1,
                ambient_light=0.8,
                visibility_range=80.0
            )
        elif weather_type == WeatherType.RAIN:
            return cls(
                particle_count=100,
                particle_size=0.8,
                particle_speed=8.0,
                particle_color=(100, 150, 255),
                particle_alpha=180,
                wind_direction=Vector3(0.2, -1.0, 0),
                wind_strength=0.5,
                fog_density=0.2,
                sound_effect="rain",
                ambient_light=0.7,
                visibility_range=60.0
            )
        elif weather_type == WeatherType.HEAVY_RAIN:
            return cls(
                particle_count=300,
                particle_size=1.0,
                particle_speed=12.0,
                particle_color=(80, 120, 255),
                particle_alpha=200,
                wind_direction=Vector3(0.4, -1.0, 0),
                wind_strength=0.8,
                fog_density=0.4,
                sound_effect="heavy_rain",
                ambient_light=0.5,
                visibility_range=40.0
            )
        elif weather_type == WeatherType.STORM:
            return cls(
                particle_count=250,
                particle_size=1.2,
                particle_speed=15.0,
                particle_color=(70, 100, 200),
                particle_alpha=220,
                wind_direction=Vector3(0.8, -1.0, 0.2),
                wind_strength=1.2,
                fog_density=0.5,
                lightning_chance=0.02,
                sound_effect="storm",
                ambient_light=0.4,
                visibility_range=30.0
            )
        elif weather_type == WeatherType.SNOW:
            return cls(
                particle_count=80,
                particle_size=0.6,
                particle_speed=2.0,
                particle_color=(240, 240, 255),
                particle_alpha=200,
                wind_direction=Vector3(0.1, -0.5, 0),
                wind_strength=0.3,
                fog_density=0.3,
                sound_effect="snow",
                ambient_light=0.8,
                visibility_range=50.0
            )
        elif weather_type == WeatherType.BLIZZARD:
            return cls(
                particle_count=250,
                particle_size=0.7,
                particle_speed=6.0,
                particle_color=(230, 230, 255),
                particle_alpha=220,
                wind_direction=Vector3(0.7, -0.7, 0.2),
                wind_strength=1.5,
                fog_density=0.7,
                sound_effect="blizzard",
                ambient_light=0.6,
                visibility_range=20.0
            )
        elif weather_type == WeatherType.FOG:
            return cls(
                particle_count=0,
                fog_density=0.8,
                fog_color=(180, 180, 180),
                wind_strength=0.1,
                ambient_light=0.7,
                visibility_range=15.0
            )
        elif weather_type == WeatherType.WINDY:
            return cls(
                particle_count=20,
                particle_size=0.5,
                particle_speed=3.0,
                particle_color=(200, 200, 150),
                particle_alpha=150,
                wind_direction=Vector3(1.0, -0.1, 0.2),
                wind_strength=1.8,
                sound_effect="wind",
                ambient_light=0.9,
                visibility_range=70.0
            )
        else:
            return cls()


class WeatherEffect:
    """Base class for weather effects"""
    
    def __init__(self, weather_system: 'WeatherSystem'):
        self.weather_system = weather_system
        self.active = False
    
    def start(self):
        """Start the effect"""
        self.active = True
    
    def stop(self):
        """Stop the effect"""
        self.active = False
    
    def update(self, delta_time: float):
        """Update the effect"""
        pass


class ParticleWeatherEffect(WeatherEffect):
    """Weather effect using particles"""
    
    def __init__(self, weather_system: 'WeatherSystem', params: WeatherParameters):
        super().__init__(weather_system)
        self.params = params
        self.particle_systems: List[ParticleSystem] = []
        self.spawn_timer = 0
        self.spawn_interval = 0.1  # Time between particle system spawns
        
        # Create initial particle systems
        self._create_particle_systems()
    
    def _create_particle_systems(self):
        """Create particle systems for the effect"""
        # Clear existing particle systems
        for ps in self.particle_systems:
            self.weather_system.engine.render_system.remove_particle_system(ps)
        
        self.particle_systems = []
        
        # Create new particle systems if needed
        if self.params.particle_count > 0:
            # Create a particle system at camera position
            camera_pos = self.weather_system.engine.render_system.camera.position
            
            # Adjust position to be above and around the camera
            spawn_pos = Vector3(
                camera_pos.x,
                camera_pos.y + 10,
                camera_pos.z
            )
            
            ps = self.weather_system.engine.create_particle_system(spawn_pos)
            ps.max_particles = self.params.particle_count
            ps.emission_rate = self.params.particle_count / 2
            
            # Customize particle system based on weather parameters
            # This would be implemented in a real particle system
            # For this example, we'll just store the parameters
            ps.set_property("weather_params", self.params)
            
            self.particle_systems.append(ps)
            ps.start()
    
    def update(self, delta_time: float):
        """Update the particle effect"""
        if not self.active:
            return
        
        # Update existing particle systems
        for ps in self.particle_systems:
            # Update position to follow camera
            camera_pos = self.weather_system.engine.render_system.camera.position
            ps.position = Vector3(
                camera_pos.x,
                camera_pos.y + 10,
                camera_pos.z
            )
            
            # Apply wind to particles
            # This would be implemented in a real particle system
            # For this example, we'll just log it
            wind_dir = self.params.wind_direction
            wind_strength = self.params.wind_strength
            
            # In a real implementation, we would modify each particle's velocity
            # based on the wind direction and strength
    
    def start(self):
        """Start the particle effect"""
        super().start()
        for ps in self.particle_systems:
            ps.start()
    
    def stop(self):
        """Stop the particle effect"""
        super().stop()
        for ps in self.particle_systems:
            ps.stop()


class LightningEffect(WeatherEffect):
    """Lightning effect for storms"""
    
    def __init__(self, weather_system: 'WeatherSystem', chance: float = 0.01):
        super().__init__(weather_system)
        self.chance = chance
        self.flash_active = False
        self.flash_duration = 0.1
        self.flash_timer = 0
        self.flash_intensity = 0.0
        self.time_until_next = random.uniform(5, 15)
    
    def update(self, delta_time: float):
        """Update the lightning effect"""
        if not self.active:
            return
        
        if self.flash_active:
            # Update flash
            self.flash_timer -= delta_time
            if self.flash_timer <= 0:
                self.flash_active = False
                # Reset ambient light
                self.weather_system.set_ambient_light(self.weather_system.current_params.ambient_light)
                
                # Play thunder sound with delay
                thunder_delay = random.uniform(0.5, 3.0)
                self.weather_system.engine.register_event_handler(
                    "thunder",
                    lambda: self.weather_system.engine.sound_system.play_sound("thunder")
                )
                # In a real implementation, we would schedule this event
                # For this example, we'll just log it
                self.weather_system.logger.info(f"Thunder will sound in {thunder_delay:.1f} seconds")
        else:
            # Check for new lightning
            self.time_until_next -= delta_time
            if self.time_until_next <= 0:
                self.trigger_lightning()
                self.time_until_next = random.uniform(5, 15)
    
    def trigger_lightning(self):
        """Trigger a lightning flash"""
        self.flash_active = True
        self.flash_timer = self.flash_duration
        self.flash_intensity = random.uniform(0.8, 1.0)
        
        # Increase ambient light for flash
        self.weather_system.set_ambient_light(self.flash_intensity)
        
        # Play lightning sound
        self.weather_system.engine.sound_system.play_sound("lightning")


class FogEffect(WeatherEffect):
    """Fog effect"""
    
    def __init__(self, weather_system: 'WeatherSystem', density: float = 0.5, color: Tuple[int, int, int] = (200, 200, 200)):
        super().__init__(weather_system)
        self.density = density
        self.color = color
        self.target_density = density
        self.current_density = 0
        self.transition_speed = 0.2  # How fast fog changes
    
    def update(self, delta_time: float):
        """Update the fog effect"""
        if not self.active:
            # Fade out fog
            self.target_density = 0
        
        # Smoothly transition to target density
        if self.current_density < self.target_density:
            self.current_density = min(self.target_density, 
                                      self.current_density + self.transition_speed * delta_time)
        elif self.current_density > self.target_density:
            self.current_density = max(self.target_density, 
                                      self.current_density - self.transition_speed * delta_time)
        
        # Apply fog to renderer
        # In a real implementation, we would set fog parameters in the renderer
        # For this example, we'll just log it
        if self.current_density > 0.01:
            self.weather_system.logger.debug(f"Fog density: {self.current_density:.2f}")
    
    def set_density(self, density: float):
        """Set fog density"""
        self.target_density = max(0, min(1, density))
    
    def set_color(self, color: Tuple[int, int, int]):
        """Set fog color"""
        self.color = color


class WeatherSystem:
    """Weather system for dynamic environmental effects"""
    
    def __init__(self, engine: Any):
        self.engine = engine
        self.current_weather = WeatherType.CLEAR
        self.current_params = WeatherParameters.create_for_weather(WeatherType.CLEAR)
        self.target_weather = WeatherType.CLEAR
        self.transition_progress = 1.0  # 0.0 to 1.0
        self.transition_duration = 10.0  # Seconds to transition
        self.time_until_change = 300.0  # Seconds until weather changes
        self.auto_change = True
        self.logger = logging.getLogger("mcp_games.engine.weather")
        
        # Weather effects
        self.particle_effect = ParticleWeatherEffect(self, self.current_params)
        self.lightning_effect = LightningEffect(self, self.current_params.lightning_chance)
        self.fog_effect = FogEffect(self, self.current_params.fog_density, self.current_params.fog_color)
        
        # Active effects
        self.active_effects: List[WeatherEffect] = []
        
        # Initialize effects for current weather
        self._activate_effects_for_weather(self.current_weather)
    
    def _activate_effects_for_weather(self, weather: WeatherType):
        """Activate appropriate effects for the weather type"""
        # Deactivate all effects first
        for effect in self.active_effects:
            effect.stop()
        
        self.active_effects = []
        
        # Get parameters for this weather
        params = WeatherParameters.create_for_weather(weather)
        
        # Activate particle effect if needed
        if params.particle_count > 0:
            self.particle_effect.params = params
            self.particle_effect.start()
            self.active_effects.append(self.particle_effect)
        
        # Activate lightning effect if needed
        if params.lightning_chance > 0:
            self.lightning_effect.chance = params.lightning_chance
            self.lightning_effect.start()
            self.active_effects.append(self.lightning_effect)
        
        # Activate fog effect if needed
        if params.fog_density > 0:
            self.fog_effect.set_density(params.fog_density)
            self.fog_effect.set_color(params.fog_color)
            self.fog_effect.start()
            self.active_effects.append(self.fog_effect)
        
        # Play weather sound if specified
        if params.sound_effect:
            self.engine.sound_system.play_sound(params.sound_effect, loops=-1)
        
        # Set ambient light
        self.set_ambient_light(params.ambient_light)
        
        # Set visibility range
        self.set_visibility_range(params.visibility_range)
    
    def set_weather(self, weather: WeatherType, transition_duration: float = 10.0):
        """Set the current weather with optional transition time"""
        if weather == self.current_weather:
            return
            
        self.target_weather = weather
        self.transition_duration = max(0.1, transition_duration)
        self.transition_progress = 0.0
        
        self.logger.info(f"Weather changing from {self.current_weather.name} to {self.target_weather.name} "
                        f"over {self.transition_duration:.1f} seconds")
    
    def set_ambient_light(self, intensity: float):
        """Set ambient light intensity"""
        # In a real implementation, we would adjust the renderer's lighting
        # For this example, we'll just log it
        self.logger.debug(f"Ambient light set to {intensity:.2f}")
    
    def set_visibility_range(self, range_value: float):
        """Set visibility range"""
        # In a real implementation, we would adjust the renderer's view distance
        # For this example, we'll just log it
        self.logger.debug(f"Visibility range set to {range_value:.1f}")
    
    def update(self, delta_time: float):
        """Update the weather system"""
        # Handle weather transitions
        if self.transition_progress < 1.0:
            # Update transition progress
            self.transition_progress += delta_time / self.transition_duration
            if self.transition_progress >= 1.0:
                # Transition complete
                self.transition_progress = 1.0
                self.current_weather = self.target_weather
                self.current_params = WeatherParameters.create_for_weather(self.current_weather)
                
                # Activate effects for new weather
                self._activate_effects_for_weather(self.current_weather)
            else:
                # During transition, interpolate parameters
                from_params = WeatherParameters.create_for_weather(self.current_weather)
                to_params = WeatherParameters.create_for_weather(self.target_weather)
                
                # Linear interpolation between parameters
                t = self.transition_progress
                self.current_params.particle_count = int(from_params.particle_count * (1-t) + to_params.particle_count * t)
                self.current_params.particle_size = from_params.particle_size * (1-t) + to_params.particle_size * t
                self.current_params.particle_speed = from_params.particle_speed * (1-t) + to_params.particle_speed * t
                self.current_params.wind_strength = from_params.wind_strength * (1-t) + to_params.wind_strength * t
                self.current_params.fog_density = from_params.fog_density * (1-t) + to_params.fog_density * t
                self.current_params.ambient_light = from_params.ambient_light * (1-t) + to_params.ambient_light * t
                self.current_params.visibility_range = from_params.visibility_range * (1-t) + to_params.visibility_range * t
                
                # Update active effects with interpolated parameters
                if self.particle_effect in self.active_effects:
                    self.particle_effect.params = self.current_params
                
                if self.fog_effect in self.active_effects:
                    self.fog_effect.set_density(self.current_params.fog_density)
                
                # Set ambient light and visibility
                self.set_ambient_light(self.current_params.ambient_light)
                self.set_visibility_range(self.current_params.visibility_range)
        
        # Auto-change weather if enabled
        if self.auto_change and self.transition_progress >= 1.0:
            self.time_until_change -= delta_time
            if self.time_until_change <= 0:
                # Choose a new random weather
                new_weather = random.choice(list(WeatherType))
                while new_weather == self.current_weather:
                    new_weather = random.choice(list(WeatherType))
                
                # Set new weather with transition
                self.set_weather(new_weather, random.uniform(10, 30))
                
                # Reset timer
                self.time_until_change = random.uniform(180, 600)  # 3-10 minutes
        
        # Update active effects
        for effect in self.active_effects:
            effect.update(delta_time)
    
    def apply_weather_effects(self, game_object: Any, delta_time: float):
        """Apply weather effects to a game object"""
        # Apply wind force to physics objects
        if hasattr(game_object, 'get_property'):
            collider = game_object.get_property('collider')
            if collider and hasattr(collider, 'game_object'):
                # Calculate wind force based on object size and wind parameters
                wind_dir = self.current_params.wind_direction
                wind_strength = self.current_params.wind_strength
                
                # In a real physics system, we would apply a force to the object
                # For this example, we'll just apply a small position offset
                if wind_strength > 0.5:  # Only apply for stronger winds
                    pos = Vector3.from_tuple(game_object.position)
                    wind_effect = wind_dir.normalize() * (wind_strength * 0.01 * delta_time)
                    new_pos = pos + wind_effect
                    game_object.position = new_pos.to_tuple()
    
    def get_weather_description(self) -> str:
        """Get a text description of the current weather"""
        if self.transition_progress < 1.0:
            return f"Changing from {self.current_weather.name} to {self.target_weather.name}"
        else:
            return self.current_weather.name