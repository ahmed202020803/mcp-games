"""
Rendering System for MCP Games using Pygame
"""

import os
import math
import pygame
from typing import Dict, List, Tuple, Any, Optional
from .physics import Vector3

# Initialize pygame
pygame.init()

class Camera:
    """Camera for 3D to 2D projection"""
    
    def __init__(self, position: Vector3 = Vector3(0, 5, -10), target: Vector3 = Vector3(0, 0, 0)):
        self.position = position
        self.target = target
        self.up = Vector3(0, 1, 0)
        self.fov = 60  # Field of view in degrees
        self.near = 0.1
        self.far = 1000.0
        
    def look_at(self, target: Vector3):
        """Point camera at target"""
        self.target = target
        
    def move(self, position: Vector3):
        """Move camera to position"""
        self.position = position
        
    def world_to_screen(self, position: Vector3, screen_width: int, screen_height: int) -> Tuple[int, int]:
        """Convert 3D world position to 2D screen position"""
        # Simple perspective projection
        direction = (position - self.position)
        
        # Calculate forward vector (normalized direction from camera to target)
        forward = (self.target - self.position).normalize()
        
        # Calculate right vector
        right = forward.cross(self.up).normalize()
        
        # Recalculate up vector to ensure orthogonality
        true_up = right.cross(forward).normalize()
        
        # Calculate dot products for projection
        x_dot = direction.dot(right)
        y_dot = direction.dot(true_up)
        z_dot = direction.dot(forward)
        
        # Skip if behind camera
        if z_dot <= 0:
            return (-1, -1)  # Off-screen
        
        # Calculate perspective projection
        aspect_ratio = screen_width / screen_height
        fov_rad = math.radians(self.fov)
        
        # Project to normalized device coordinates
        x_ndc = x_dot / (z_dot * math.tan(fov_rad / 2) * aspect_ratio)
        y_ndc = y_dot / (z_dot * math.tan(fov_rad / 2))
        
        # Convert to screen coordinates
        x_screen = int((x_ndc + 1) * 0.5 * screen_width)
        y_screen = int((1 - (y_ndc + 1) * 0.5) * screen_height)
        
        return (x_screen, y_screen)


class Sprite:
    """2D sprite for rendering"""
    
    def __init__(self, image_path: str, scale: float = 1.0):
        self.original_image = None
        self.image = None
        self.scale = scale
        self.load_image(image_path)
        
    def load_image(self, image_path: str):
        """Load image from file"""
        try:
            if os.path.exists(image_path):
                self.original_image = pygame.image.load(image_path).convert_alpha()
                self.resize(self.scale)
            else:
                # Create a default colored rectangle if image not found
                self.original_image = pygame.Surface((32, 32), pygame.SRCALPHA)
                self.original_image.fill((255, 0, 255))  # Magenta for missing textures
                pygame.draw.rect(self.original_image, (0, 0, 0), pygame.Rect(0, 0, 32, 32), 1)
                self.resize(self.scale)
        except pygame.error:
            # Create a default colored rectangle if loading fails
            self.original_image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.original_image.fill((255, 0, 255))  # Magenta for missing textures
            pygame.draw.rect(self.original_image, (0, 0, 0), pygame.Rect(0, 0, 32, 32), 1)
            self.resize(self.scale)
    
    def resize(self, scale: float):
        """Resize the sprite"""
        if self.original_image:
            width = int(self.original_image.get_width() * scale)
            height = int(self.original_image.get_height() * scale)
            self.image = pygame.transform.scale(self.original_image, (width, height))


class RenderComponent:
    """Component for rendering game objects"""
    
    def __init__(self, game_object: Any, sprite_path: str = None):
        self.game_object = game_object
        self.sprite = None
        self.color = (255, 255, 255)  # Default color
        self.visible = True
        self.layer = 0  # Rendering layer/order
        self.scale = 1.0
        
        if sprite_path:
            self.set_sprite(sprite_path)
    
    def set_sprite(self, sprite_path: str):
        """Set the sprite for this component"""
        self.sprite = Sprite(sprite_path, self.scale)
    
    def set_color(self, color: Tuple[int, int, int]):
        """Set the color for this component"""
        self.color = color
    
    def set_scale(self, scale: float):
        """Set the scale for this component"""
        self.scale = scale
        if self.sprite:
            self.sprite.resize(scale)


class ParticleSystem:
    """Simple particle system for visual effects"""
    
    class Particle:
        """Individual particle"""
        def __init__(self, position: Vector3, velocity: Vector3, color: Tuple[int, int, int], 
                     size: float, lifetime: float):
            self.position = position
            self.velocity = velocity
            self.color = color
            self.size = size
            self.lifetime = lifetime
            self.age = 0
            self.alive = True
        
        def update(self, delta_time: float):
            """Update particle state"""
            self.position = self.position + (self.velocity * delta_time)
            self.age += delta_time
            
            # Fade out based on lifetime
            if self.age >= self.lifetime:
                self.alive = False
    
    def __init__(self, position: Vector3 = Vector3()):
        self.position = position
        self.particles: List[ParticleSystem.Particle] = []
        self.max_particles = 100
        self.emission_rate = 10  # Particles per second
        self.emission_timer = 0
        self.active = False
    
    def emit(self, count: int = 1):
        """Emit particles"""
        import random
        
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            # Random velocity in a sphere
            angle1 = random.uniform(0, math.pi * 2)
            angle2 = random.uniform(0, math.pi)
            speed = random.uniform(1, 3)
            
            vx = math.sin(angle2) * math.cos(angle1) * speed
            vy = math.sin(angle2) * math.sin(angle1) * speed
            vz = math.cos(angle2) * speed
            
            # Random color variations
            r = min(255, max(0, random.randint(200, 255)))
            g = min(255, max(0, random.randint(100, 200)))
            b = min(255, max(0, random.randint(0, 100)))
            
            # Create particle
            particle = self.Particle(
                position=Vector3(self.position.x, self.position.y, self.position.z),
                velocity=Vector3(vx, vy, vz),
                color=(r, g, b),
                size=random.uniform(2, 5),
                lifetime=random.uniform(0.5, 2.0)
            )
            
            self.particles.append(particle)
    
    def update(self, delta_time: float):
        """Update all particles"""
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
        
        # Update remaining particles
        for particle in self.particles:
            particle.update(delta_time)
        
        # Emit new particles if active
        if self.active:
            self.emission_timer += delta_time
            to_emit = int(self.emission_rate * self.emission_timer)
            if to_emit > 0:
                self.emit(to_emit)
                self.emission_timer -= to_emit / self.emission_rate
    
    def start(self):
        """Start emitting particles"""
        self.active = True
    
    def stop(self):
        """Stop emitting particles"""
        self.active = False


class RenderSystem:
    """Rendering system for game objects"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600, title: str = "MCP Game"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption(title)
        
        self.camera = Camera()
        self.render_components: List[RenderComponent] = []
        self.particle_systems: List[ParticleSystem] = []
        self.background_color = (0, 0, 0)  # Black background
        self.debug_mode = False
        
        # Font for debug text
        self.font = pygame.font.SysFont(None, 24)
    
    def add_render_component(self, component: RenderComponent):
        """Add a render component to the system"""
        self.render_components.append(component)
        # Sort by layer
        self.render_components.sort(key=lambda c: c.layer)
    
    def remove_render_component(self, component: RenderComponent):
        """Remove a render component from the system"""
        if component in self.render_components:
            self.render_components.remove(component)
    
    def add_particle_system(self, particle_system: ParticleSystem):
        """Add a particle system to the renderer"""
        self.particle_systems.append(particle_system)
    
    def remove_particle_system(self, particle_system: ParticleSystem):
        """Remove a particle system from the renderer"""
        if particle_system in self.particle_systems:
            self.particle_systems.remove(particle_system)
    
    def set_camera(self, camera: Camera):
        """Set the active camera"""
        self.camera = camera
    
    def set_background_color(self, color: Tuple[int, int, int]):
        """Set the background color"""
        self.background_color = color
    
    def toggle_debug_mode(self):
        """Toggle debug rendering"""
        self.debug_mode = not self.debug_mode
    
    def render(self):
        """Render all visible components"""
        # Clear screen
        self.screen.fill(self.background_color)
        
        # Render game objects
        for component in self.render_components:
            if not component.visible:
                continue
                
            # Get world position
            world_pos = Vector3.from_tuple(component.game_object.position)
            
            # Convert to screen position
            screen_pos = self.camera.world_to_screen(world_pos, self.screen_width, self.screen_height)
            
            # Skip if off-screen
            if screen_pos[0] < 0 or screen_pos[1] < 0 or \
               screen_pos[0] > self.screen_width or screen_pos[1] > self.screen_height:
                continue
            
            # Render sprite if available
            if component.sprite and component.sprite.image:
                # Calculate sprite position (centered)
                sprite_rect = component.sprite.image.get_rect()
                sprite_rect.center = screen_pos
                
                # Draw sprite
                self.screen.blit(component.sprite.image, sprite_rect)
            else:
                # Draw a simple circle if no sprite
                pygame.draw.circle(self.screen, component.color, screen_pos, 10 * component.scale)
        
        # Render particles
        for particle_system in self.particle_systems:
            for particle in particle_system.particles:
                # Convert to screen position
                screen_pos = self.camera.world_to_screen(
                    particle.position, self.screen_width, self.screen_height
                )
                
                # Skip if off-screen
                if screen_pos[0] < 0 or screen_pos[1] < 0 or \
                   screen_pos[0] > self.screen_width or screen_pos[1] > self.screen_height:
                    continue
                
                # Calculate alpha based on lifetime
                alpha = 255 * (1 - (particle.age / particle.lifetime))
                color = (*particle.color, int(alpha))
                
                # Draw particle
                pygame.draw.circle(
                    self.screen, 
                    color, 
                    screen_pos, 
                    particle.size
                )
        
        # Debug rendering
        if self.debug_mode:
            fps = int(pygame.time.Clock().get_fps())
            fps_text = self.font.render(f"FPS: {fps}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))
            
            # Object count
            obj_text = self.font.render(f"Objects: {len(self.render_components)}", True, (255, 255, 255))
            self.screen.blit(obj_text, (10, 40))
            
            # Particle count
            total_particles = sum(len(ps.particles) for ps in self.particle_systems)
            particle_text = self.font.render(f"Particles: {total_particles}", True, (255, 255, 255))
            self.screen.blit(particle_text, (10, 70))
        
        # Update display
        pygame.display.flip()