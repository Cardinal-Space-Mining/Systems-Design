import math
import random

# Material properties (e.g., steel)
E = 210e9             # Young's modulus (Pa)
nu = 0.3              # Poisson's ratio (dimensionless)
G = E / (2 * (1+nu))  # Shear modulus (Pa) for completeness
density = 7850        # Density (kg/m^3)
yield_stress = 250e6  # Yield strength (Pa)

class Frame:
    """Frame geometry with nodes and members for optimization."""
    # Bounds for design variables
    MIN_WIDTH = 1.0    # m
    MAX_WIDTH = 10.0   # m
    MIN_HEIGHT = 1.0   # m
    MAX_HEIGHT = 10.0  # m
    MIN_AREA = 1e-4    # m^2 (to avoid zero)
    MAX_AREA = 1.0     # m^2

    def __init__(self, width, height, area_left, area_right, area_base):
        # Geometry variables
        self.width = width
        self.height = height
        # Cross-sectional areas for members
        self.area_left = area_left    # left leg
        self.area_right = area_right  # right leg
        self.area_base = area_base    # base tie
        # Define node coordinates (assuming symmetric frame)
        self.nodes = {
            "N_left": (0.0, 0.0, 0.0),
            "N_right": (self.width, 0.0, 0.0),
            "N_top": (self.width/2.0, self.height, 0.0)
        }
        # Member connections (each as tuple of (node_i, node_j, area))
        self.members = [
            ("N_left", "N_top", "LeftSec"),    # left leg
            ("N_right", "N_top", "RightSec"),  # right leg
            ("N_left", "N_right", "BaseSec")   # base tie
        ]

    @staticmethod
    def random_frame():
        """Generate a Frame with random geometry within bounds."""
        w = random.uniform(Frame.MIN_WIDTH, Frame.MAX_WIDTH)
        h = random.uniform(Frame.MIN_HEIGHT, Frame.MAX_HEIGHT)
        # Random areas for each member within bounds
        a_left = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        a_right = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        a_base = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        return Frame(w, h, a_left, a_right, a_base)

    def mutate(self, mutation_rate=0.1):
        """Randomly perturb the frame's design variables (in-place)."""
        # Mutate width and height
        if random.random() < mutation_rate:
            delta_w = (self.MAX_WIDTH - self.MIN_WIDTH) * 0.1
            self.width += random.uniform(-delta_w, delta_w)
            # Keep within bounds
            self.width = max(self.MIN_WIDTH, min(self.width, self.MAX_WIDTH))
        if random.random() < mutation_rate:
            delta_h = (self.MAX_HEIGHT - self.MIN_HEIGHT) * 0.1
            self.height += random.uniform(-delta_h, delta_h)
            self.height = max(self.MIN_HEIGHT, min(self.height, self.MAX_HEIGHT))
        # Mutate cross-sectional areas
        for attr in ["area_left", "area_right", "area_base"]:
            if random.random() < mutation_rate:
                val = getattr(self, attr)
                delta_a = (self.MAX_AREA - self.MIN_AREA) * 0.1
                val += random.uniform(-delta_a, delta_a)
                val = max(self.MIN_AREA, min(val, self.MAX_AREA))
                setattr(self, attr, val)
        # Update node positions after mutation
        self.nodes["N_right"] = (self.width, 0.0, 0.0)
        self.nodes["N_top"] = (self.width/2.0, self.height, 0.0)

    def calc_mass(self):
        """Calculate total mass of the frame (kg)."""
        # Member lengths
        left_len = math.sqrt((self.width/2.0)**2 + (self.height)**2)
        right_len = left_len  # symmetric
        base_len = self.width
        # Volume = area * length, Mass = density * volume
        mass = (self.area_left * left_len + 
                self.area_right * right_len + 
                self.area_base * base_len) * density
        return mass

    def __repr__(self):
        return (f"Frame(width={self.width:.2f}, height={self.height:.2f}, "
                f"areas=[{self.area_left:.4f}, {self.area_right:.4f}, {self.area_base:.4f}])")