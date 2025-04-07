"""
Frame Class for Structural Optimization
=======================================

This module defines a Frame class to represent the geometry and material properties
of a planar truss frame. The goal is to minimize the frame mass subject to stress and
deflection constraints using finite element analysis (FEA) and a genetic algorithm (GA).

Key Features:
-------------
- Triangular frame structure (two inclined legs and a horizontal tie).
- Design variables: width, height, cross-sectional areas of each member.
- Mutate method allows bounded random perturbation of variables for GA use.
- Mass is calculated as total volume * material density.
- Geometry is symmetric; left and right legs share structural layout.

Geometric Constraints:
----------------------
Bounds are enforced on all design variables to ensure physical validity:
- Width, height ∈ [1.0 m, 10.0 m]
- Area ∈ [1e-4 m^2, 1.0 m^2] (non-zero minimum to prevent singularities)

Material Assumptions:
---------------------
- Material: Steel (E = 210 GPa, ν = 0.3, ρ = 7850 kg/m³, σ_y = 250 MPa)

This class is used in combination with a PyNite-based FEA solver and a GA optimizer
for lightweight frame design under load.
"""
import math
import random

# Material properties (e.g., steel)
E = 210e9             # Young's modulus (Pa)
nu = 0.3              # Poisson's ratio (dimensionless)
G = E / (2 * (1+nu))  # Shear modulus (Pa)
density = 7850        # Density (kg/m^3)
yield_stress = 250e6  # Yield strength (Pa)

class Frame:
    """Frame geometry with nodes and members for optimization."""

    # Bounds for design variables
    MIN_WIDTH = 1.0    # Minimum frame width (m)
    MAX_WIDTH = 10.0   # Maximum frame width (m)
    MIN_HEIGHT = 1.0   # Minimum frame height (m)
    MAX_HEIGHT = 10.0  # Maximum frame height (m)
    MIN_AREA = 1e-4    # Minimum cross-sectional area (m^2)
    MAX_AREA = 1.0     # Maximum cross-sectional area (m^2)

    def __init__(self, width, height, area_left, area_right, area_base):
        # Frame geometry (width and height define node positions)
        self.width = width
        self.height = height
        # Cross-sectional areas for each truss member
        self.area_left = area_left    # left leg
        self.area_right = area_right  # right leg
        self.area_base = area_base    # base tie
        # Define node coordinates (assuming symmetric triangular frame)
        self.nodes = {
            "N_left": (0.0, 0.0, 0.0),
            "N_right": (self.width, 0.0, 0.0),
            "N_top": (self.width/2.0, self.height, 0.0)
        }
        # Define members as tuples of (start_node, end_node, section_name)
        self.members = [
            ("N_left", "N_top", "LeftSec"),    # left leg
            ("N_right", "N_top", "RightSec"),  # right leg
            ("N_left", "N_right", "BaseSec")   # base tie
        ]

    @staticmethod
    def random_frame():
        """Generate a Frame with random geometry and area within defined bounds.

        Used for initializing the population in the genetic algorithm.
        """
        w = random.uniform(Frame.MIN_WIDTH, Frame.MAX_WIDTH)
        h = random.uniform(Frame.MIN_HEIGHT, Frame.MAX_HEIGHT)
        a_left = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        a_right = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        a_base = random.uniform(Frame.MIN_AREA, Frame.MAX_AREA)
        return Frame(w, h, a_left, a_right, a_base)

    def mutate(self, mutation_rate=0.1):
        """Randomly perturb the frame's design variables within their bounds.

        This introduces diversity into the population for the GA and helps
        escape local minima. Each variable has a chance (mutation_rate)
        to be perturbed by up to 10% of its range.
        """
        # Mutate width
        if random.random() < mutation_rate:
            delta_w = (self.MAX_WIDTH - self.MIN_WIDTH) * 0.1
            self.width += random.uniform(-delta_w, delta_w)
            self.width = max(self.MIN_WIDTH, min(self.width, self.MAX_WIDTH))
        # Mutate height
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
        """Calculate the total mass of the frame based on member volumes and density.

        This is the objective function for the optimization.
        """
        # Compute member lengths
        left_len = math.sqrt((self.width/2.0)**2 + (self.height)**2)
        right_len = left_len  # symmetry
        base_len = self.width
        # Mass = density * (area * length) for each member
        mass = (self.area_left * left_len + 
                self.area_right * right_len + 
                self.area_base * base_len) * density
        return mass

    def __repr__(self):
        """Readable representation of frame parameters."""
        return (f"Frame(width={self.width:.2f}, height={self.height:.2f}, "
                f"areas=[{self.area_left:.4f}, {self.area_right:.4f}, {self.area_base:.4f}])")
