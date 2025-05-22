import pygame
import random

class MatrixEffect:
    """
    Creates a Matrix-style falling character effect for the background
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont('consolas', 14)
        self.chars = "01010101010101010101010101010101"
        self.streams = []
        self.density = 1.0  # Density factor (1.0 = normal, higher = more streams)
        self.color_scheme = "cyan_purple"  # Default color scheme
        self.message_display = False
        self.message_time = 0
        self.message_duration = 5000  # 5 seconds
        self.message_interval = 15000  # 15 seconds between messages
        self.last_message_time = 0
        self.setup_streams()
        
    def setup_streams(self):
        # Create character streams
        self.streams = []
        stream_spacing = 20  # Space streams every 20 pixels
        
        # Calculate number of streams based on density
        num_streams = int((self.screen_width / stream_spacing) * self.density)
        
        for i in range(num_streams):
            # Calculate x position with even spacing
            x = int(i * (self.screen_width / num_streams))
            
            # Each stream has: x position, y position, speed, characters
            stream = {
                'x': x,
                'y': random.randint(-100, 0),
                'speed': random.randint(5, 15),
                'length': random.randint(5, 30),
                'chars': []
            }
            
            # Generate random characters for this stream
            for j in range(stream['length']):
                char_index = random.randint(0, len(self.chars) - 1)
                stream['chars'].append(self.chars[char_index])
            
            self.streams.append(stream)
    
    def set_density(self, density):
        """Change the density of the matrix effect and regenerate streams"""
        self.density = max(0.5, min(2.0, density))  # Clamp between 0.5 and 2.0
        self.setup_streams()
    
    def set_color_scheme(self, scheme):
        """Set the color scheme for the matrix effect"""
        self.color_scheme = scheme
    
    def get_color(self, brightness, alpha=255):
        """Get color based on the current color scheme and brightness"""
        if self.color_scheme == "green":
            return (0, brightness, 0, alpha)
        elif self.color_scheme == "cyan_purple":
            # Create a gradient from cyan to purple based on brightness
            # Enhanced purple component for more vibrant effect
            cyan_component = int(brightness * 0.7)
            purple_component = int(brightness * 0.8)
            return (purple_component, cyan_component, brightness, alpha)
        elif self.color_scheme == "blue":
            return (0, brightness // 2, brightness, alpha)
        else:
            # Default to green
            return (0, brightness, 0, alpha)
    
    def update(self):
        # Update each stream's position
        for stream in self.streams:
            stream['y'] += stream['speed'] / 10
            
            # If stream is off screen, reset it
            if stream['y'] > self.screen_height:
                stream['y'] = random.randint(-200, -50)
                stream['speed'] = random.randint(5, 15)
                
            # Randomly change characters
            if random.random() < 0.02:  # 2% chance per frame
                for i in range(len(stream['chars'])):
                    if random.random() < 0.1:  # 10% chance per character
                        char_index = random.randint(0, len(self.chars) - 1)
                        stream['chars'][i] = self.chars[char_index]
        
        # Check if it's time to display a message
        current_time = pygame.time.get_ticks()
        if not self.message_display and current_time - self.last_message_time > self.message_interval:
            self.message_display = True
            self.message_time = current_time
            self.last_message_time = current_time
        
        # Check if message display time is over
        if self.message_display and current_time - self.message_time > self.message_duration:
            self.message_display = False
    
    def render(self, surface, alpha=128):
        # Create a transparent surface for the matrix effect
        matrix_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Draw each stream
        for stream in self.streams:
            for i, char in enumerate(stream['chars']):
                y_pos = int(stream['y']) + i * 15
                
                # Only draw if on screen
                if 0 <= y_pos < self.screen_height:
                    # Fade brightness based on position in stream
                    brightness = 255 - (i * (255 // max(1, stream['length'])))
                    color = self.get_color(brightness, alpha)
                    
                    # First character is brighter
                    if i == 0:
                        bright_color = self.get_color(255, alpha)
                        color = bright_color
                    
                    char_surface = self.font.render(char, True, color)
                    matrix_surface.blit(char_surface, (stream['x'], y_pos))
        
        # Draw "CypherCore" message periodically
        if self.message_display:
            message = "CypherCore"
            message_font = pygame.font.SysFont('consolas', 40)
            
            # Calculate position to center the message
            message_surface = message_font.render(message, True, self.get_color(255, 200))
            message_x = self.screen_width // 2 - message_surface.get_width() // 2
            message_y = self.screen_height // 2 - message_surface.get_height() // 2
            
            # Add a subtle glow effect
            glow_size = 3
            for offset in range(1, glow_size + 1):
                glow_alpha = 100 - (offset * 30)
                glow_surface = message_font.render(message, True, self.get_color(255, glow_alpha))
                matrix_surface.blit(glow_surface, (message_x - offset, message_y))
                matrix_surface.blit(glow_surface, (message_x + offset, message_y))
                matrix_surface.blit(glow_surface, (message_x, message_y - offset))
                matrix_surface.blit(glow_surface, (message_x, message_y + offset))
            
            # Draw the main message
            matrix_surface.blit(message_surface, (message_x, message_y))
        
        # Blit the matrix surface onto the main surface
        surface.blit(matrix_surface, (0, 0))
        
    def render_glitch(self, surface, glitch_intensity=0.05):
        """Render the matrix effect with occasional glitches"""
        # First render the normal matrix effect
        self.render(surface)
        
        # Add random glitch effects
        if random.random() < glitch_intensity:
            # Create horizontal glitch lines
            num_lines = random.randint(1, 5)
            for _ in range(num_lines):
                y = random.randint(0, self.screen_height - 10)  # Ensure within bounds
                height = random.randint(2, 8)
                offset = random.randint(-10, 10)
                
                # Make sure the rectangle is within bounds
                if y + height > self.screen_height:
                    height = self.screen_height - y
                
                # Get a portion of the screen
                try:
                    line_rect = pygame.Rect(0, y, self.screen_width, height)
                    line_surface = surface.subsurface(line_rect).copy()
                    
                    # Draw it with offset
                    surface.blit(line_surface, (offset, y))
                except ValueError:
                    # Skip if out of bounds
                    pass
            
            # Increased chance of color distortion with more purple tones
            if random.random() < 0.5:  # Increased from 0.3 to 0.5
                glitch_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                # More purple-focused color options
                color = random.choice([
                    (255, 0, 255, 30),  # Magenta
                    (180, 0, 255, 30),  # Purple
                    (100, 0, 255, 30),  # Deep purple
                    (255, 0, 128, 30)   # Pink-purple
                ])
                glitch_surface.fill(color)
                surface.blit(glitch_surface, (0, 0))
                
            # Occasionally add vertical glitch lines for more effect
            if random.random() < 0.3:
                num_v_lines = random.randint(1, 3)
                for _ in range(num_v_lines):
                    x = random.randint(0, self.screen_width - 10)
                    width = random.randint(2, 8)
                    offset = random.randint(-10, 10)
                    
                    if x + width > self.screen_width:
                        width = self.screen_width - x
                    
                    try:
                        v_line_rect = pygame.Rect(x, 0, width, self.screen_height)
                        v_line_surface = surface.subsurface(v_line_rect).copy()
                        surface.blit(v_line_surface, (x, offset))
                    except ValueError:
                        pass
