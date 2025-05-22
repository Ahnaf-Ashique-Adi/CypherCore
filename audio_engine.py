import pygame
import os

class AudioEngine:
    """
    Handles all game audio including music and sound effects
    """
    def __init__(self):
        # Initialize pygame mixer if not already done
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Sound volume levels
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        
        # Dictionaries to store loaded sounds
        self.music = {}
        self.sounds = {}
        
        # Create sounds directory if it doesn't exist
        os.makedirs('sounds', exist_ok=True)
        
        # Generate simple sounds for testing
        self.generate_simple_sounds()
    
    def generate_simple_sounds(self):
        """Generate very simple sounds using pygame's built-in capabilities"""
        try:
            # Create a simple click sound
            click_sound = pygame.mixer.Sound(self.generate_simple_beep(880, 0.05))
            self.sounds['click'] = click_sound
            self.sounds['click'].set_volume(self.sfx_volume)
            
            # Create a simple success sound
            success_sound = pygame.mixer.Sound(self.generate_simple_beep(440, 0.1))
            self.sounds['success'] = success_sound
            self.sounds['success'].set_volume(self.sfx_volume)
            
            # Create a simple failure sound
            failure_sound = pygame.mixer.Sound(self.generate_simple_beep(220, 0.2))
            self.sounds['failure'] = failure_sound
            self.sounds['failure'].set_volume(self.sfx_volume)
            
        except Exception as e:
            print(f"Could not generate sounds: {e}")
    
    def generate_simple_beep(self, frequency, duration):
        """Generate a very simple beep sound"""
        # This is a very basic sound generator
        import array
        import math
        
        sample_rate = 22050
        n_samples = int(round(duration * sample_rate))
        
        # Generate a square wave (very simple)
        buf = array.array('h', [0] * n_samples)
        for i in range(n_samples):
            if int(i / sample_rate * frequency * 2) % 2:
                buf[i] = 10000  # Square wave amplitude
            else:
                buf[i] = -10000
        
        return buf
    
    def load_sound(self, name, file_path):
        """Load a sound effect from file"""
        try:
            self.sounds[name] = pygame.mixer.Sound(file_path)
            self.sounds[name].set_volume(self.sfx_volume)
        except pygame.error as e:
            print(f"Could not load sound {file_path}: {e}")
    
    def load_music(self, name, file_path):
        """Store music file path for later playing"""
        self.music[name] = file_path
    
    def play_sound(self, name):
        """Play a sound effect"""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            # Silent fallback if sound not found
            pass
    
    def play_music(self, name, loops=-1):
        """Play background music"""
        if name in self.music:
            try:
                pygame.mixer.music.load(self.music[name])
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
            except pygame.error as e:
                print(f"Could not play music {self.music[name]}: {e}")
    
    def stop_music(self):
        """Stop currently playing music"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
