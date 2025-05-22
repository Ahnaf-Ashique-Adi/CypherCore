import pygame
import random
import math
from abc import ABC, abstractmethod

class Puzzle(ABC):
    """Abstract base class for all puzzle levels"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.completed = False
        self.font = pygame.font.SysFont('consolas', 20)
    
    @abstractmethod
    def handle_event(self, event):
        """Handle pygame events"""
        pass
    
    @abstractmethod
    def update(self):
        """Update puzzle state"""
        pass
    
    @abstractmethod
    def render(self, surface):
        """Render puzzle to the given surface"""
        pass
    
    def is_completed(self):
        """Check if puzzle is completed"""
        return self.completed


class BinaryMaze(Puzzle):
    """Level 1: Binary Maze puzzle"""
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.grid_size = 20  # Increased from 15 to 20
        self.cell_size = 25  # Decreased to fit larger grid
        self.grid = self.generate_maze()
        self.player_pos = [0, 0]  # Start position
        self.exit_pos = [self.grid_size-1, self.grid_size-1]  # End position
        self.time_limit = 300  # Increased to 5 minutes
        self.start_time = pygame.time.get_ticks()
        self.path_hint = self.generate_path_hint()
        
        # Trap mechanics
        self.trap_tiles = []
        self.generate_traps()
        self.trap_triggered = False
        self.trap_time = 0
        self.trap_penalty = 5000  # 5 second penalty
        
        # Player history for reset mechanics
        self.player_history = [self.player_pos.copy()]
        self.max_history = 10  # Remember last 10 positions
        
        # Visual effects
        self.flash_effect = False
        self.flash_time = 0
        self.flash_duration = 500  # milliseconds
    
    def generate_maze(self):
        """Generate a more complex binary maze"""
        import random
        grid = []
        
        # Create a base grid with more walls
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                # Create a maze with more walls (1) than open paths (0)
                # Ensure start and end are always open
                if (i == 0 and j == 0) or (i == self.grid_size-1 and j == self.grid_size-1):
                    row.append(0)
                else:
                    # 40% chance of wall
                    row.append(1 if random.random() < 0.4 else 0)
            grid.append(row)
        
        # Ensure there's a path from start to end
        self.ensure_path(grid)
        return grid
    
    def ensure_path(self, grid):
        """Create a guaranteed path from start to end"""
        # This uses a simple algorithm to carve a path
        # A real game would use a proper maze generation algorithm
        
        # Start at the beginning
        current_pos = [0, 0]
        target_pos = [self.grid_size-1, self.grid_size-1]
        
        # Create a winding path to the target
        while current_pos != target_pos:
            # Decide whether to move horizontally or vertically
            if random.random() < 0.5:
                # Move horizontally if possible
                if current_pos[1] < target_pos[1]:
                    current_pos[1] += 1
                elif current_pos[1] > 0:
                    current_pos[1] -= 1
            else:
                # Move vertically if possible
                if current_pos[0] < target_pos[0]:
                    current_pos[0] += 1
                elif current_pos[0] > 0:
                    current_pos[0] -= 1
            
            # Clear the current position
            grid[current_pos[0]][current_pos[1]] = 0
            
            # Sometimes create a branch path
            if random.random() < 0.2:
                branch_pos = current_pos.copy()
                
                # Choose a random direction for the branch
                direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                branch_pos[0] += direction[0]
                branch_pos[1] += direction[1]
                
                # Make sure branch is within bounds
                if (0 <= branch_pos[0] < self.grid_size and 
                    0 <= branch_pos[1] < self.grid_size):
                    grid[branch_pos[0]][branch_pos[1]] = 0
    
    def generate_path_hint(self):
        """Generate a path from start to end for hints"""
        # In a real game, this would use A* or similar algorithm
        path = []
        current = [0, 0]
        visited = set()
        visited.add((current[0], current[1]))
        
        # Simple breadth-first search
        queue = [[current]]
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            # Check if we've reached the exit
            if current == self.exit_pos:
                return path
            
            # Try all four directions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                
                # Check if the new position is valid
                if (0 <= nx < self.grid_size and 
                    0 <= ny < self.grid_size and 
                    self.grid[nx][ny] == 0 and
                    (nx, ny) not in visited):
                    
                    new_path = list(path)
                    new_path.append([nx, ny])
                    queue.append(new_path)
                    visited.add((nx, ny))
        
        # If no path found, return a simple path
        return [[0, 0], [self.grid_size-1, self.grid_size-1]]
    
    def generate_traps(self):
        """Generate trap tiles that penalize the player"""
        import random
        
        # Clear existing traps
        self.trap_tiles = []
        
        # Number of traps scales with grid size
        num_traps = self.grid_size // 2
        
        # Place traps on open tiles, avoiding start, end, and the hint path
        safe_tiles = set((pos[0], pos[1]) for pos in self.path_hint)
        safe_tiles.add((0, 0))  # Start
        safe_tiles.add((self.grid_size-1, self.grid_size-1))  # End
        
        for _ in range(num_traps):
            # Try to find a valid trap location
            for _ in range(50):  # Limit attempts to avoid infinite loop
                x = random.randint(0, self.grid_size-1)
                y = random.randint(0, self.grid_size-1)
                
                # Check if this is a valid trap location
                if (self.grid[x][y] == 0 and  # Open tile
                    (x, y) not in safe_tiles and  # Not on safe path
                    [x, y] not in self.trap_tiles):  # Not already a trap
                    
                    self.trap_tiles.append([x, y])
                    break
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Don't allow movement during trap penalty
            if self.trap_triggered and pygame.time.get_ticks() - self.trap_time < self.trap_penalty:
                return
                
            new_pos = self.player_pos.copy()
            
            if event.key == pygame.K_UP:
                new_pos[0] -= 1
            elif event.key == pygame.K_DOWN:
                new_pos[0] += 1
            elif event.key == pygame.K_LEFT:
                new_pos[1] -= 1
            elif event.key == pygame.K_RIGHT:
                new_pos[1] += 1
            
            # Check if the new position is valid
            if (0 <= new_pos[0] < self.grid_size and 
                0 <= new_pos[1] < self.grid_size and
                self.grid[new_pos[0]][new_pos[1]] == 0):
                
                # Update player position
                self.player_pos = new_pos
                
                # Add to history
                self.player_history.append(self.player_pos.copy())
                if len(self.player_history) > self.max_history:
                    self.player_history.pop(0)
                
                # Check if player stepped on a trap
                if self.player_pos in self.trap_tiles:
                    self.trigger_trap()
    
    def trigger_trap(self):
        """Trigger trap effects"""
        self.trap_triggered = True
        self.trap_time = pygame.time.get_ticks()
        self.flash_effect = True
        self.flash_time = pygame.time.get_ticks()
        
        # Reset player to previous safe position if available
        if len(self.player_history) > 1:
            # Go back 2 positions (current + previous)
            self.player_pos = self.player_history[-2].copy()
    
    def update(self):
        # Check if player reached the exit
        if self.player_pos == self.exit_pos:
            self.completed = True
        
        # Update trap status
        if self.trap_triggered:
            if pygame.time.get_ticks() - self.trap_time >= self.trap_penalty:
                self.trap_triggered = False
        
        # Update flash effect
        if self.flash_effect:
            if pygame.time.get_ticks() - self.flash_time >= self.flash_duration:
                self.flash_effect = False
                
        # No time limit check - let player continue indefinitely
    
    def render(self, surface):
        # Calculate grid offset to center it
        offset_x = (self.screen_width - self.grid_size * self.cell_size) // 2
        offset_y = (self.screen_height - self.grid_size * self.cell_size) // 2
        
        # Draw grid
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell_color = (0, 0, 0) if self.grid[i][j] == 1 else (20, 20, 20)
                
                # Highlight path hint (fading based on time)
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                if [i, j] in self.path_hint and elapsed_time < 5:  # Reduced from 10 to 5 seconds
                    hint_alpha = max(0, 255 - int(elapsed_time * 51))  # Fade twice as fast
                    cell_color = (0, hint_alpha // 3, 0)
                
                # Draw cell
                pygame.draw.rect(
                    surface, 
                    cell_color, 
                    (offset_x + j * self.cell_size, 
                     offset_y + i * self.cell_size, 
                     self.cell_size, self.cell_size)
                )
                
                # Draw cell border
                pygame.draw.rect(
                    surface, 
                    (0, 50, 0), 
                    (offset_x + j * self.cell_size, 
                     offset_y + i * self.cell_size, 
                     self.cell_size, self.cell_size),
                    1
                )
                
                # Draw binary value
                if self.grid[i][j] == 0 or self.grid[i][j] == 1:
                    text = self.font.render(str(self.grid[i][j]), True, (0, 255, 0))
                    surface.blit(
                        text, 
                        (offset_x + j * self.cell_size + self.cell_size // 2 - text.get_width() // 2, 
                         offset_y + i * self.cell_size + self.cell_size // 2 - text.get_height() // 2)
                    )
        
        # Draw traps (subtle indication)
        for trap in self.trap_tiles:
            # Only show traps after the hint time has passed
            elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
            if elapsed_time > 5:  # After hint fades
                pygame.draw.rect(
                    surface, 
                    (50, 0, 0),  # Dark red
                    (offset_x + trap[1] * self.cell_size, 
                     offset_y + trap[0] * self.cell_size, 
                     self.cell_size, self.cell_size),
                    1  # Border only
                )
        
        # Draw player
        pygame.draw.rect(
            surface, 
            (0, 255, 0), 
            (offset_x + self.player_pos[1] * self.cell_size + 5, 
             offset_y + self.player_pos[0] * self.cell_size + 5, 
             self.cell_size - 10, self.cell_size - 10)
        )
        
        # Draw exit
        pygame.draw.rect(
            surface, 
            (0, 100, 255), 
            (offset_x + self.exit_pos[1] * self.cell_size + 5, 
             offset_y + self.exit_pos[0] * self.cell_size + 5, 
             self.cell_size - 10, self.cell_size - 10)
        )
        
        # Draw timer - only show if less than 60 seconds remaining
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, self.time_limit - elapsed_time)
        
        if time_left < 60:
            timer_text = self.font.render(f"Time: {int(time_left)}s", True, (255, 50, 50))
        else:
            # Show minutes and seconds for longer timers
            minutes = int(time_left) // 60
            seconds = int(time_left) % 60
            timer_text = self.font.render(f"Time: {minutes}:{seconds:02d}", True, (0, 255, 0))
        
        surface.blit(timer_text, (20, 20))
        
        # Draw trap penalty indicator
        if self.trap_triggered:
            penalty_left = (self.trap_penalty - (pygame.time.get_ticks() - self.trap_time)) / 1000
            if penalty_left > 0:
                penalty_text = self.font.render(f"TRAP! Penalty: {penalty_left:.1f}s", True, (255, 0, 0))
                surface.blit(penalty_text, (20, 50))
        
        # Flash effect when trap is triggered
        if self.flash_effect:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            alpha = 128 * (1 - (pygame.time.get_ticks() - self.flash_time) / self.flash_duration)
            flash_surface.fill((255, 0, 0, int(alpha)))
            surface.blit(flash_surface, (0, 0))
        
        # Draw instructions
        instr_text = self.font.render("Use arrow keys to navigate the binary maze", True, (0, 255, 0))
        surface.blit(instr_text, (20, self.screen_height - 40))


class LogicGatePuzzle(Puzzle):
    """Level 2: Logic Gate Puzzle"""
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.completed = False
        self.font_small = pygame.font.SysFont('consolas', 16)
        
        # Circuit components
        self.components = []
        self.wires = []
        self.inputs = []
        self.outputs = []
        
        # Interaction state
        self.selected_component = None
        self.dragging = False
        self.drag_offset = (0, 0)
        
        # Level state
        self.level_complete = False
        self.level_failed = False
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 300  # Increased to 5 minutes
        
        # Puzzle variants
        self.puzzle_variants = [
            self.generate_puzzle_1,  # Original puzzle
            self.generate_puzzle_2,  # New variant
            self.generate_puzzle_3   # Another variant
        ]
        
        # Select a random puzzle variant
        puzzle_generator = random.choice(self.puzzle_variants)
        puzzle_generator()
    
    def generate_puzzle_1(self):
        """Generate the first logic gate puzzle variant"""
        # Clear existing components
        self.components = []
        self.wires = []
        self.inputs = []
        self.outputs = []
        
        # Define input nodes (binary values that can be toggled)
        input1 = {
            'type': 'input',
            'value': 0,  # 0 or 1
            'rect': pygame.Rect(100, 150, 40, 40),
            'label': 'A',
            'output_pos': (140, 170)
        }
        
        input2 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 250, 40, 40),
            'label': 'B',
            'output_pos': (140, 270)
        }
        
        input3 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 350, 40, 40),
            'label': 'C',
            'output_pos': (140, 370)
        }
        
        input4 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 450, 40, 40),
            'label': 'D',
            'output_pos': (140, 470)
        }
        
        self.inputs = [input1, input2, input3, input4]
        
        # Define logic gates
        and_gate1 = {
            'type': 'gate',
            'gate_type': 'AND',
            'rect': pygame.Rect(250, 200, 60, 60),
            'inputs': [],  # Will be connected via wires
            'input_pos': [(250, 210), (250, 250)],
            'output_pos': (310, 230),
            'result': 0  # Computed result
        }
        
        or_gate = {
            'type': 'gate',
            'gate_type': 'OR',
            'rect': pygame.Rect(250, 350, 60, 60),
            'inputs': [],
            'input_pos': [(250, 360), (250, 400)],
            'output_pos': (310, 380),
            'result': 0
        }
        
        not_gate = {
            'type': 'gate',
            'gate_type': 'NOT',
            'rect': pygame.Rect(400, 280, 60, 60),
            'inputs': [],
            'input_pos': [(400, 310)],
            'output_pos': (460, 310),
            'result': 0
        }
        
        xor_gate = {
            'type': 'gate',
            'gate_type': 'XOR',
            'rect': pygame.Rect(400, 400, 60, 60),
            'inputs': [],
            'input_pos': [(400, 410), (400, 450)],
            'output_pos': (460, 430),
            'result': 0
        }
        
        and_gate2 = {
            'type': 'gate',
            'gate_type': 'AND',
            'rect': pygame.Rect(520, 350, 60, 60),
            'inputs': [],
            'input_pos': [(520, 360), (520, 400)],
            'output_pos': (580, 380),
            'result': 0
        }
        
        self.components = [and_gate1, or_gate, not_gate, xor_gate, and_gate2]
        
        # Define output node (goal)
        output = {
            'type': 'output',
            'value': 0,  # Current value
            'target': 1,  # Target value to win
            'rect': pygame.Rect(650, 350, 40, 40),
            'label': 'OUT',
            'input_pos': (650, 370)
        }
        
        self.outputs = [output]
        
        # Define initial wires
        self.wires = [
            # Connect input A to AND gate 1 input 1
            {
                'from_component': input1,
                'to_component': and_gate1,
                'from_pos': input1['output_pos'],
                'to_pos': and_gate1['input_pos'][0],
                'value': 0
            },
            # Connect input B to AND gate 1 input 2
            {
                'from_component': input2,
                'to_component': and_gate1,
                'from_pos': input2['output_pos'],
                'to_pos': and_gate1['input_pos'][1],
                'value': 0
            },
            # Connect input C to OR gate input 1
            {
                'from_component': input3,
                'to_component': or_gate,
                'from_pos': input3['output_pos'],
                'to_pos': or_gate['input_pos'][0],
                'value': 0
            },
            # Connect input D to OR gate input 2
            {
                'from_component': input4,
                'to_component': or_gate,
                'from_pos': input4['output_pos'],
                'to_pos': or_gate['input_pos'][1],
                'value': 0
            },
            # Connect AND gate 1 output to NOT gate input
            {
                'from_component': and_gate1,
                'to_component': not_gate,
                'from_pos': and_gate1['output_pos'],
                'to_pos': not_gate['input_pos'][0],
                'value': 0
            },
            # Connect OR gate output to XOR gate input 1
            {
                'from_component': or_gate,
                'to_component': xor_gate,
                'from_pos': or_gate['output_pos'],
                'to_pos': xor_gate['input_pos'][0],
                'value': 0
            },
            # Connect NOT gate output to XOR gate input 2
            {
                'from_component': not_gate,
                'to_component': xor_gate,
                'from_pos': not_gate['output_pos'],
                'to_pos': xor_gate['input_pos'][1],
                'value': 0
            },
            # Connect NOT gate output to AND gate 2 input 1
            {
                'from_component': not_gate,
                'to_component': and_gate2,
                'from_pos': not_gate['output_pos'],
                'to_pos': and_gate2['input_pos'][0],
                'value': 0
            },
            # Connect XOR gate output to AND gate 2 input 2
            {
                'from_component': xor_gate,
                'to_component': and_gate2,
                'from_pos': xor_gate['output_pos'],
                'to_pos': and_gate2['input_pos'][1],
                'value': 0
            },
            # Connect AND gate 2 output to final output
            {
                'from_component': and_gate2,
                'to_component': output,
                'from_pos': and_gate2['output_pos'],
                'to_pos': output['input_pos'],
                'value': 0
            }
        ]
        
        # Update component inputs based on wires
        self.update_component_inputs()
    
    def generate_puzzle_2(self):
        """Generate the second logic gate puzzle variant - NAND implementation"""
        # Clear existing components
        self.components = []
        self.wires = []
        self.inputs = []
        self.outputs = []
        
        # Define input nodes
        input1 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 150, 40, 40),
            'label': 'A',
            'output_pos': (140, 170)
        }
        
        input2 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 250, 40, 40),
            'label': 'B',
            'output_pos': (140, 270)
        }
        
        input3 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 350, 40, 40),
            'label': 'C',
            'output_pos': (140, 370)
        }
        
        self.inputs = [input1, input2, input3]
        
        # Define logic gates for a NAND-based circuit
        and_gate1 = {
            'type': 'gate',
            'gate_type': 'AND',
            'rect': pygame.Rect(250, 200, 60, 60),
            'inputs': [],
            'input_pos': [(250, 210), (250, 250)],
            'output_pos': (310, 230),
            'result': 0
        }
        
        not_gate1 = {
            'type': 'gate',
            'gate_type': 'NOT',
            'rect': pygame.Rect(350, 200, 60, 60),
            'inputs': [],
            'input_pos': [(350, 230)],
            'output_pos': (410, 230),
            'result': 0
        }
        
        and_gate2 = {
            'type': 'gate',
            'gate_type': 'AND',
            'rect': pygame.Rect(250, 350, 60, 60),
            'inputs': [],
            'input_pos': [(250, 360), (250, 400)],
            'output_pos': (310, 380),
            'result': 0
        }
        
        not_gate2 = {
            'type': 'gate',
            'gate_type': 'NOT',
            'rect': pygame.Rect(350, 350, 60, 60),
            'inputs': [],
            'input_pos': [(350, 380)],
            'output_pos': (410, 380),
            'result': 0
        }
        
        or_gate = {
            'type': 'gate',
            'gate_type': 'OR',
            'rect': pygame.Rect(500, 275, 60, 60),
            'inputs': [],
            'input_pos': [(500, 285), (500, 325)],
            'output_pos': (560, 305),
            'result': 0
        }
        
        self.components = [and_gate1, not_gate1, and_gate2, not_gate2, or_gate]
        
        # Define output node
        output = {
            'type': 'output',
            'value': 0,
            'target': 1,
            'rect': pygame.Rect(650, 275, 40, 40),
            'label': 'OUT',
            'input_pos': (650, 295)
        }
        
        self.outputs = [output]
        
        # Define wires for NAND implementation
        self.wires = [
            # Connect input A to AND gate 1 input 1
            {
                'from_component': input1,
                'to_component': and_gate1,
                'from_pos': input1['output_pos'],
                'to_pos': and_gate1['input_pos'][0],
                'value': 0
            },
            # Connect input B to AND gate 1 input 2
            {
                'from_component': input2,
                'to_component': and_gate1,
                'from_pos': input2['output_pos'],
                'to_pos': and_gate1['input_pos'][1],
                'value': 0
            },
            # Connect AND gate 1 to NOT gate 1 (creating NAND)
            {
                'from_component': and_gate1,
                'to_component': not_gate1,
                'from_pos': and_gate1['output_pos'],
                'to_pos': not_gate1['input_pos'][0],
                'value': 0
            },
            # Connect input B to AND gate 2 input 1
            {
                'from_component': input2,
                'to_component': and_gate2,
                'from_pos': input2['output_pos'],
                'to_pos': and_gate2['input_pos'][0],
                'value': 0
            },
            # Connect input C to AND gate 2 input 2
            {
                'from_component': input3,
                'to_component': and_gate2,
                'from_pos': input3['output_pos'],
                'to_pos': and_gate2['input_pos'][1],
                'value': 0
            },
            # Connect AND gate 2 to NOT gate 2 (creating NAND)
            {
                'from_component': and_gate2,
                'to_component': not_gate2,
                'from_pos': and_gate2['output_pos'],
                'to_pos': not_gate2['input_pos'][0],
                'value': 0
            },
            # Connect NOT gate 1 to OR gate input 1
            {
                'from_component': not_gate1,
                'to_component': or_gate,
                'from_pos': not_gate1['output_pos'],
                'to_pos': or_gate['input_pos'][0],
                'value': 0
            },
            # Connect NOT gate 2 to OR gate input 2
            {
                'from_component': not_gate2,
                'to_component': or_gate,
                'from_pos': not_gate2['output_pos'],
                'to_pos': or_gate['input_pos'][1],
                'value': 0
            },
            # Connect OR gate to output
            {
                'from_component': or_gate,
                'to_component': output,
                'from_pos': or_gate['output_pos'],
                'to_pos': output['input_pos'],
                'value': 0
            }
        ]
        
        # Update component inputs based on wires
        self.update_component_inputs()
    
    def generate_puzzle_3(self):
        """Generate the third logic gate puzzle variant - XOR-based circuit"""
        # Clear existing components
        self.components = []
        self.wires = []
        self.inputs = []
        self.outputs = []
        
        # Define input nodes
        input1 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 200, 40, 40),
            'label': 'A',
            'output_pos': (140, 220)
        }
        
        input2 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 300, 40, 40),
            'label': 'B',
            'output_pos': (140, 320)
        }
        
        input3 = {
            'type': 'input',
            'value': 0,
            'rect': pygame.Rect(100, 400, 40, 40),
            'label': 'C',
            'output_pos': (140, 420)
        }
        
        self.inputs = [input1, input2, input3]
        
        # Define logic gates for XOR-based circuit
        xor_gate1 = {
            'type': 'gate',
            'gate_type': 'XOR',
            'rect': pygame.Rect(250, 250, 60, 60),
            'inputs': [],
            'input_pos': [(250, 260), (250, 300)],
            'output_pos': (310, 280),
            'result': 0
        }
        
        xor_gate2 = {
            'type': 'gate',
            'gate_type': 'XOR',
            'rect': pygame.Rect(400, 320, 60, 60),
            'inputs': [],
            'input_pos': [(400, 330), (400, 370)],
            'output_pos': (460, 350),
            'result': 0
        }
        
        and_gate = {
            'type': 'gate',
            'gate_type': 'AND',
            'rect': pygame.Rect(550, 300, 60, 60),
            'inputs': [],
            'input_pos': [(550, 310), (550, 350)],
            'output_pos': (610, 330),
            'result': 0
        }
        
        self.components = [xor_gate1, xor_gate2, and_gate]
        
        # Define output node
        output = {
            'type': 'output',
            'value': 0,
            'target': 1,
            'rect': pygame.Rect(700, 300, 40, 40),
            'label': 'OUT',
            'input_pos': (700, 320)
        }
        
        self.outputs = [output]
        
        # Define wires for XOR-based circuit
        self.wires = [
            # Connect input A to XOR gate 1 input 1
            {
                'from_component': input1,
                'to_component': xor_gate1,
                'from_pos': input1['output_pos'],
                'to_pos': xor_gate1['input_pos'][0],
                'value': 0
            },
            # Connect input B to XOR gate 1 input 2
            {
                'from_component': input2,
                'to_component': xor_gate1,
                'from_pos': input2['output_pos'],
                'to_pos': xor_gate1['input_pos'][1],
                'value': 0
            },
            # Connect XOR gate 1 output to XOR gate 2 input 1
            {
                'from_component': xor_gate1,
                'to_component': xor_gate2,
                'from_pos': xor_gate1['output_pos'],
                'to_pos': xor_gate2['input_pos'][0],
                'value': 0
            },
            # Connect input C to XOR gate 2 input 2
            {
                'from_component': input3,
                'to_component': xor_gate2,
                'from_pos': input3['output_pos'],
                'to_pos': xor_gate2['input_pos'][1],
                'value': 0
            },
            # Connect input A to AND gate input 1
            {
                'from_component': input1,
                'to_component': and_gate,
                'from_pos': input1['output_pos'],
                'to_pos': and_gate['input_pos'][0],
                'value': 0
            },
            # Connect XOR gate 2 output to AND gate input 2
            {
                'from_component': xor_gate2,
                'to_component': and_gate,
                'from_pos': xor_gate2['output_pos'],
                'to_pos': and_gate['input_pos'][1],
                'value': 0
            },
            # Connect AND gate output to final output
            {
                'from_component': and_gate,
                'to_component': output,
                'from_pos': and_gate['output_pos'],
                'to_pos': output['input_pos'],
                'value': 0
            }
        ]
        
        # Update component inputs based on wires
        self.update_component_inputs()
    
    def generate_puzzle(self):
        """Legacy method for backward compatibility"""
        self.generate_puzzle_1()
    
    def update_component_inputs(self):
        """Update the inputs list for each component based on wires"""
        # Clear all inputs
        for component in self.components:
            component['inputs'] = []
        
        for output in self.outputs:
            output['inputs'] = []
        
        # Add inputs based on wires
        for wire in self.wires:
            if wire['to_component']['type'] == 'gate':
                wire['to_component']['inputs'].append(wire['from_component'])
            elif wire['to_component']['type'] == 'output':
                wire['to_component']['inputs'].append(wire['from_component'])
    
    def evaluate_circuit(self):
        """Evaluate the entire circuit and update component values"""
        # First, propagate input values to wires
        for wire in self.wires:
            if wire['from_component']['type'] == 'input':
                wire['value'] = wire['from_component']['value']
        
        # Evaluate gates in order (this is simplified; a real circuit would need topological sorting)
        for component in self.components:
            # Get input values from wires
            input_values = []
            for wire in self.wires:
                if wire['to_component'] == component:
                    input_values.append(wire['value'])
            
            # Evaluate gate based on type
            if component['gate_type'] == 'AND':
                # AND gate: output is 1 only if all inputs are 1
                component['result'] = 1 if all(v == 1 for v in input_values) else 0
            elif component['gate_type'] == 'OR':
                # OR gate: output is 1 if any input is 1
                component['result'] = 1 if any(v == 1 for v in input_values) else 0
            elif component['gate_type'] == 'NOT':
                # NOT gate: inverts the input
                if input_values:
                    component['result'] = 1 if input_values[0] == 0 else 0
                else:
                    component['result'] = 0
            elif component['gate_type'] == 'XOR':
                # XOR gate: output is 1 if odd number of inputs are 1
                component['result'] = 1 if sum(input_values) % 2 == 1 else 0
            
            # Propagate result to outgoing wires
            for wire in self.wires:
                if wire['from_component'] == component:
                    wire['value'] = component['result']
        
        # Finally, update output values
        for output in self.outputs:
            # Get input value from wire
            for wire in self.wires:
                if wire['to_component'] == output:
                    output['value'] = wire['value']
            
            # Check if output matches target
            if output['value'] == output['target']:
                self.level_complete = True
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check if clicked on an input node to toggle it
                mouse_pos = pygame.mouse.get_pos()
                for input_node in self.inputs:
                    if input_node['rect'].collidepoint(mouse_pos):
                        # Toggle input value
                        input_node['value'] = 1 if input_node['value'] == 0 else 0
                        # Re-evaluate circuit
                        self.evaluate_circuit()
                        break
                
                # Check if clicked on a gate to drag it
                for component in self.components:
                    if component['rect'].collidepoint(mouse_pos):
                        self.selected_component = component
                        self.dragging = True
                        self.drag_offset = (
                            component['rect'].x - mouse_pos[0],
                            component['rect'].y - mouse_pos[1]
                        )
                        break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                self.dragging = False
                self.selected_component = None
                # Re-evaluate circuit after moving components
                self.evaluate_circuit()
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.selected_component:
                # Move the component
                mouse_pos = pygame.mouse.get_pos()
                self.selected_component['rect'].x = mouse_pos[0] + self.drag_offset[0]
                self.selected_component['rect'].y = mouse_pos[1] + self.drag_offset[1]
                
                # Update connection points
                if self.selected_component['type'] == 'gate':
                    gate_type = self.selected_component['gate_type']
                    rect = self.selected_component['rect']
                    
                    # Update input positions
                    if gate_type == 'AND' or gate_type == 'OR':
                        self.selected_component['input_pos'] = [
                            (rect.x, rect.y + 10),
                            (rect.x, rect.y + rect.height - 10)
                        ]
                        self.selected_component['output_pos'] = (rect.x + rect.width, rect.y + rect.height // 2)
                    elif gate_type == 'NOT':
                        self.selected_component['input_pos'] = [(rect.x, rect.y + rect.height // 2)]
                        self.selected_component['output_pos'] = (rect.x + rect.width, rect.y + rect.height // 2)
                
                # Update wire positions
                for wire in self.wires:
                    if wire['from_component'] == self.selected_component:
                        wire['from_pos'] = self.selected_component['output_pos']
                    if wire['to_component'] == self.selected_component:
                        # Find which input this wire connects to
                        if self.selected_component['type'] == 'gate':
                            for i, input_pos in enumerate(self.selected_component['input_pos']):
                                # This is a simplification; in a real game you'd track which input is connected
                                if i < len(self.selected_component['input_pos']):
                                    wire['to_pos'] = self.selected_component['input_pos'][i]
                                    break
                        else:
                            wire['to_pos'] = self.selected_component['input_pos']
    
    def update(self):
        # Check if level is completed
        if self.level_complete:
            self.completed = True
            
        # No time limit check - let player continue indefinitely
    
    def render(self, surface):
        # Draw background
        pygame.draw.rect(surface, (10, 10, 20), (0, 0, self.screen_width, self.screen_height))
        
        # Draw title
        title_text = self.font.render("Logic Gate Puzzle", True, (0, 255, 0))
        surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw instructions
        instr_text = self.font_small.render("Click inputs to toggle values. Drag gates to rearrange. Make output = 1", True, (0, 200, 0))
        surface.blit(instr_text, (self.screen_width // 2 - instr_text.get_width() // 2, 60))
        
        # Draw wires first (so they appear behind components)
        for wire in self.wires:
            # Wire color based on signal value
            color = (0, 255, 0) if wire['value'] == 1 else (100, 100, 100)
            
            # Draw wire as a line with a slight curve
            start_pos = wire['from_pos']
            end_pos = wire['to_pos']
            mid_x = (start_pos[0] + end_pos[0]) // 2
            
            # Draw as three connected lines for a simple curve effect
            pygame.draw.line(surface, color, start_pos, (mid_x, start_pos[1]), 2)
            pygame.draw.line(surface, color, (mid_x, start_pos[1]), (mid_x, end_pos[1]), 2)
            pygame.draw.line(surface, color, (mid_x, end_pos[1]), end_pos, 2)
        
        # Draw input nodes
        for input_node in self.inputs:
            # Color based on value
            color = (0, 255, 0) if input_node['value'] == 1 else (100, 100, 100)
            
            # Draw input node
            pygame.draw.rect(surface, color, input_node['rect'], 2)
            
            # Draw label
            label_text = self.font.render(input_node['label'], True, color)
            surface.blit(label_text, (input_node['rect'].x + 5, input_node['rect'].y - 25))
            
            # Draw value
            value_text = self.font.render(str(input_node['value']), True, color)
            surface.blit(value_text, (input_node['rect'].x + 15, input_node['rect'].y + 10))
        
        # Draw logic gates
        for component in self.components:
            # Draw gate
            pygame.draw.rect(surface, (0, 150, 150), component['rect'], 2)
            
            # Draw gate type
            gate_text = self.font.render(component['gate_type'], True, (0, 200, 200))
            surface.blit(gate_text, (component['rect'].x + 5, component['rect'].y + 20))
        
        # Draw output node
        for output in self.outputs:
            # Color based on whether output matches target
            color = (0, 255, 0) if output['value'] == output['target'] else (255, 50, 50)
            
            # Draw output node
            pygame.draw.rect(surface, color, output['rect'], 2)
            
            # Draw label
            label_text = self.font.render(output['label'], True, color)
            surface.blit(label_text, (output['rect'].x - 10, output['rect'].y - 25))
            
            # Draw current value and target
            value_text = self.font.render(f"{output['value']} / Target: {output['target']}", True, color)
            surface.blit(value_text, (output['rect'].x - 20, output['rect'].y + 50))
        
        # Draw timer
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, self.time_limit - elapsed_time)
        timer_text = self.font.render(f"Time: {int(time_left)}s", True, (0, 255, 0))
        surface.blit(timer_text, (20, 20))
        
        # Draw completion message
        if self.level_complete:
            complete_text = self.font.render("Circuit Complete! Well done!", True, (0, 255, 0))
            surface.blit(complete_text, (self.screen_width // 2 - complete_text.get_width() // 2, 500))
        
        # Draw failure message
        if self.level_failed:
            fail_text = self.font.render("Time's up! Try again.", True, (255, 0, 0))
            surface.blit(fail_text, (self.screen_width // 2 - fail_text.get_width() // 2, 500))


class MemoryDecryption(Puzzle):
    """Level 3: Memory Decryption"""
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.grid_size = 4  # 4x4 grid of memory tiles
        self.tile_size = 80
        self.grid = []
        self.selected_tiles = []
        self.matched_pairs = []
        self.show_all = False
        self.show_all_time = 0
        self.show_duration = 3000  # Show all tiles for 3 seconds at start
        self.reveal_duration = 1000  # How long to show mismatched tiles
        self.reveal_time = 0
        self.completed = False
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 300  # Increased to 5 minutes
        self.generate_grid()
    
    def generate_grid(self):
        """Generate a grid of memory tiles with matching pairs"""
        # Create pairs of symbols (using hex codes for simplicity)
        symbols = ['0x01', '0x02', '0x03', '0x04', '0x05', '0x06', '0x07', '0x08']
        pairs = symbols + symbols  # Each symbol appears twice
        
        # Shuffle the pairs
        random.shuffle(pairs)
        
        # Create the grid
        self.grid = []
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                index = i * self.grid_size + j
                if index < len(pairs):
                    tile = {
                        'symbol': pairs[index],
                        'revealed': False,
                        'matched': False,
                        'rect': pygame.Rect(
                            self.screen_width // 2 - (self.grid_size * self.tile_size) // 2 + j * self.tile_size,
                            self.screen_height // 2 - (self.grid_size * self.tile_size) // 2 + i * self.tile_size,
                            self.tile_size - 10,
                            self.tile_size - 10
                        )
                    }
                    row.append(tile)
            self.grid.append(row)
        
        # Show all tiles at the beginning
        self.show_all = True
        self.show_all_time = pygame.time.get_ticks()
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Only allow clicking if not showing all tiles and not revealing a mismatch
            if not self.show_all and (len(self.selected_tiles) < 2 or pygame.time.get_ticks() - self.reveal_time > self.reveal_duration):
                mouse_pos = pygame.mouse.get_pos()
                
                # Reset selected tiles if we've shown a mismatch long enough
                if len(self.selected_tiles) == 2 and pygame.time.get_ticks() - self.reveal_time > self.reveal_duration:
                    for tile in self.selected_tiles:
                        if not tile['matched']:
                            tile['revealed'] = False
                    self.selected_tiles = []
                
                # Check if a tile was clicked
                for row in self.grid:
                    for tile in row:
                        if tile['rect'].collidepoint(mouse_pos) and not tile['matched'] and not tile['revealed']:
                            # Reveal the tile
                            tile['revealed'] = True
                            self.selected_tiles.append(tile)
                            
                            # Check if two tiles are selected
                            if len(self.selected_tiles) == 2:
                                # Check if they match
                                if self.selected_tiles[0]['symbol'] == self.selected_tiles[1]['symbol']:
                                    # Match found
                                    self.selected_tiles[0]['matched'] = True
                                    self.selected_tiles[1]['matched'] = True
                                    self.matched_pairs.append(self.selected_tiles.copy())
                                    self.selected_tiles = []
                                    
                                    # Check if all pairs are matched
                                    all_matched = True
                                    for r in self.grid:
                                        for t in r:
                                            if not t['matched']:
                                                all_matched = False
                                                break
                                    
                                    if all_matched:
                                        self.completed = True
                                else:
                                    # No match, start reveal timer
                                    self.reveal_time = pygame.time.get_ticks()
                            
                            # Only process one tile per click
                            return
    
    def update(self):
        # Check if initial reveal time is over
        if self.show_all and pygame.time.get_ticks() - self.show_all_time > self.show_duration:
            self.show_all = False
            # Hide all tiles
            for row in self.grid:
                for tile in row:
                    tile['revealed'] = False
        
        # Check if mismatched tiles should be hidden
        if len(self.selected_tiles) == 2 and pygame.time.get_ticks() - self.reveal_time > self.reveal_duration:
            # Hide mismatched tiles
            for tile in self.selected_tiles:
                if not tile['matched']:
                    tile['revealed'] = False
            self.selected_tiles = []
            
        # No time limit check - let player continue indefinitely
    
    def render(self, surface):
        # Draw background
        pygame.draw.rect(surface, (10, 10, 20), (0, 0, self.screen_width, self.screen_height))
        
        # Draw title
        title_text = self.font.render("Memory Decryption", True, (0, 255, 0))
        surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw grid
        for row in self.grid:
            for tile in row:
                # Determine tile color
                if tile['matched']:
                    color = (0, 200, 0)  # Green for matched
                elif tile['revealed'] or self.show_all:
                    color = (0, 150, 150)  # Cyan for revealed
                else:
                    color = (50, 50, 50)  # Dark gray for hidden
                
                # Draw tile background
                pygame.draw.rect(surface, color, tile['rect'])
                
                # Draw tile border
                pygame.draw.rect(surface, (0, 255, 0), tile['rect'], 2)
                
                # Draw symbol if revealed or showing all
                if tile['revealed'] or self.show_all or tile['matched']:
                    symbol_text = self.font.render(tile['symbol'], True, (0, 0, 0))
                    surface.blit(
                        symbol_text,
                        (tile['rect'].x + tile['rect'].width // 2 - symbol_text.get_width() // 2,
                         tile['rect'].y + tile['rect'].height // 2 - symbol_text.get_height() // 2)
                    )
        
        # Draw timer
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, self.time_limit - elapsed_time)
        timer_text = self.font.render(f"Time: {int(time_left)}s", True, (0, 255, 0))
        surface.blit(timer_text, (20, 20))
        
        # Draw instructions
        if self.show_all and pygame.time.get_ticks() - self.show_all_time < self.show_duration:
            instr_text = self.font.render("Memorize the patterns!", True, (0, 255, 0))
            surface.blit(instr_text, (self.screen_width // 2 - instr_text.get_width() // 2, self.screen_height - 50))
        else:
            instr_text = self.font.render("Click tiles to reveal and match pairs", True, (0, 255, 0))
            surface.blit(instr_text, (self.screen_width // 2 - instr_text.get_width() // 2, self.screen_height - 50))
        
        # Draw completion message
        if self.completed:
            complete_text = self.font.render("Memory Decrypted! Access Granted!", True, (0, 255, 0))
            surface.blit(complete_text, (self.screen_width // 2 - complete_text.get_width() // 2, self.screen_height - 80))


class CoreBreachTiming(Puzzle):
    """Level 4: Core Breach Timing"""
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        self.completed = False
        self.start_time = pygame.time.get_ticks()
        self.time_limit = 300  # Increased to 5 minutes
        self.center_pos = (screen_width // 2, screen_height // 2)
        self.core_radius = 100
        self.orbit_radius = 200
        self.nodes = []
        self.active_node = None
        self.active_time = 0
        self.active_duration = 1500  # How long a node stays active
        self.sequence = []
        self.current_sequence_index = 0
        self.sequence_complete = False
        self.rotation_speed = 0.5  # Degrees per frame
        self.current_angle = 0
        self.success_flashes = 0
        self.flash_time = 0
        self.generate_nodes()
        self.generate_sequence()
    
    def generate_nodes(self):
        """Generate nodes that orbit the core"""
        num_nodes = 8
        for i in range(num_nodes):
            angle = i * (360 / num_nodes)
            x = self.center_pos[0] + self.orbit_radius * math.cos(math.radians(angle))
            y = self.center_pos[1] + self.orbit_radius * math.sin(math.radians(angle))
            
            node = {
                'id': i,
                'pos': (int(x), int(y)),
                'angle': angle,
                'radius': 30,
                'active': False,
                'hit': False,
                'color': (0, 150, 150)
            }
            self.nodes.append(node)
    
    def generate_sequence(self):
        """Generate a sequence of nodes to activate"""
        import random
        
        # Create a sequence of node IDs
        sequence_length = 5  # Start with 5 nodes
        self.sequence = []
        for _ in range(sequence_length):
            self.sequence.append(random.randint(0, len(self.nodes) - 1))
        
        # Activate the first node
        self.activate_next_node()
    
    def activate_next_node(self):
        """Activate the next node in the sequence"""
        if self.current_sequence_index < len(self.sequence):
            node_id = self.sequence[self.current_sequence_index]
            self.nodes[node_id]['active'] = True
            self.active_node = self.nodes[node_id]
            self.active_time = pygame.time.get_ticks()
        else:
            self.sequence_complete = True
            self.completed = True
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked on the active node
            mouse_pos = pygame.mouse.get_pos()
            if self.active_node:
                dx = mouse_pos[0] - self.active_node['pos'][0]
                dy = mouse_pos[1] - self.active_node['pos'][1]
                distance = (dx*dx + dy*dy) ** 0.5
                
                if distance <= self.active_node['radius']:
                    # Hit the active node
                    self.active_node['hit'] = True
                    self.active_node['active'] = False
                    self.active_node['color'] = (0, 255, 0)  # Green for success
                    self.current_sequence_index += 1
                    self.success_flashes = 3
                    self.flash_time = pygame.time.get_ticks()
                    
                    # Activate next node after a short delay
                    pygame.time.set_timer(pygame.USEREVENT, 500)
                else:
                    # Missed the active node
                    if self.active_node:
                        self.active_node['color'] = (255, 0, 0)  # Red for failure
                        self.active_node['active'] = False
                        
                        # Reset the sequence
                        self.current_sequence_index = 0
                        pygame.time.set_timer(pygame.USEREVENT, 1000)
        
        elif event.type == pygame.USEREVENT:
            # Timer event for activating next node
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Cancel the timer
            self.activate_next_node()
    
    def update(self):
        # Update node positions based on rotation
        self.current_angle += self.rotation_speed
        if self.current_angle >= 360:
            self.current_angle -= 360
        
        for node in self.nodes:
            angle = node['angle'] + self.current_angle
            x = self.center_pos[0] + self.orbit_radius * math.cos(math.radians(angle))
            y = self.center_pos[1] + self.orbit_radius * math.sin(math.radians(angle))
            node['pos'] = (int(x), int(y))
        
        # Check if active node timed out
        if self.active_node and pygame.time.get_ticks() - self.active_time > self.active_duration:
            self.active_node['active'] = False
            self.active_node['color'] = (255, 0, 0)  # Red for failure
            
            # Reset the sequence
            self.current_sequence_index = 0
            self.activate_next_node()
        
        # Update success flash
        if self.success_flashes > 0 and pygame.time.get_ticks() - self.flash_time > 200:
            self.success_flashes -= 1
            self.flash_time = pygame.time.get_ticks()
            
        # No time limit check - let player continue indefinitely
    
    def render(self, surface):
        # Draw background
        pygame.draw.rect(surface, (10, 10, 20), (0, 0, self.screen_width, self.screen_height))
        
        # Draw title
        title_text = self.font.render("Core Breach Timing", True, (0, 255, 0))
        surface.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 20))
        
        # Draw core
        core_color = (0, 255, 0) if self.success_flashes % 2 == 0 else (255, 255, 255)
        pygame.draw.circle(surface, core_color, self.center_pos, self.core_radius)
        pygame.draw.circle(surface, (0, 0, 0), self.center_pos, self.core_radius - 10)
        
        # Draw orbit path
        pygame.draw.circle(surface, (30, 30, 30), self.center_pos, self.orbit_radius, 1)
        
        # Draw nodes
        for node in self.nodes:
            # Draw node
            pygame.draw.circle(surface, node['color'], node['pos'], node['radius'])
            
            # Draw node ID
            id_text = self.font.render(str(node['id']), True, (0, 0, 0))
            surface.blit(
                id_text,
                (node['pos'][0] - id_text.get_width() // 2,
                 node['pos'][1] - id_text.get_height() // 2)
            )
            
            # Draw active indicator
            if node['active']:
                pygame.draw.circle(surface, (255, 255, 0), node['pos'], node['radius'] + 5, 3)
        
        # Draw sequence progress
        progress_text = self.font.render(
            f"Sequence: {self.current_sequence_index}/{len(self.sequence)}", 
            True, 
            (0, 255, 0)
        )
        surface.blit(progress_text, (20, 60))
        
        # Draw timer
        elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
        time_left = max(0, self.time_limit - elapsed_time)
        timer_text = self.font.render(f"Time: {int(time_left)}s", True, (0, 255, 0))
        surface.blit(timer_text, (20, 20))
        
        # Draw instructions
        instr_text = self.font.render("Click the highlighted nodes in sequence before they time out", True, (0, 255, 0))
        surface.blit(instr_text, (self.screen_width // 2 - instr_text.get_width() // 2, self.screen_height - 50))
        
        # Draw completion message
        if self.sequence_complete:
            complete_text = self.font.render("Core Breached! System Access Granted!", True, (0, 255, 0))
            surface.blit(complete_text, (self.screen_width // 2 - complete_text.get_width() // 2, self.screen_height - 80))


class LevelManager:
    """Manages game levels and transitions"""
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = 0
        self.levels = [
            BinaryMaze(screen_width, screen_height),
            LogicGatePuzzle(screen_width, screen_height),
            MemoryDecryption(screen_width, screen_height),
            CoreBreachTiming(screen_width, screen_height)
        ]
        self.transition_time = 0
        self.in_transition = False
        self.font = pygame.font.SysFont('consolas', 30)
    
    def handle_event(self, event):
        if not self.in_transition and self.current_level < len(self.levels):
            self.levels[self.current_level].handle_event(event)
    
    def update(self):
        if self.in_transition:
            # Handle transition animation
            if pygame.time.get_ticks() - self.transition_time > 2000:  # 2 second transition
                self.in_transition = False
        elif self.current_level < len(self.levels):
            # Update current level
            self.levels[self.current_level].update()
            
            # Check if level is completed
            if self.levels[self.current_level].is_completed():
                self.start_transition()
    
    def start_transition(self):
        self.in_transition = True
        self.transition_time = pygame.time.get_ticks()
        self.current_level += 1
    
    def render(self, surface):
        if self.in_transition:
            # Render transition screen
            level_text = "Level Complete!"
            if self.current_level < len(self.levels):
                level_text += f" Preparing Level {self.current_level + 1}..."
            else:
                level_text = "All Levels Complete! You've mastered CypherCore!"
            
            text = self.font.render(level_text, True, (0, 255, 0))
            surface.blit(text, (self.screen_width // 2 - text.get_width() // 2, self.screen_height // 2))
        elif self.current_level < len(self.levels):
            # Render current level
            self.levels[self.current_level].render(surface)
        else:
            # Game complete
            text = self.font.render("Congratulations! You've completed CypherCore!", True, (0, 255, 0))
            surface.blit(text, (self.screen_width // 2 - text.get_width() // 2, self.screen_height // 2))
