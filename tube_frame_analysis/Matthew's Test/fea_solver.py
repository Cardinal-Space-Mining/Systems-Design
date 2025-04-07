# fea_solver.py
"""
FEA Solver for Frame Analysis using PyNite
===========================================

This module uses the PyNiteFEA library to perform 3D finite element analysis
on a planar truss frame. It simulates the structural response of a triangular
frame under a vertical load applied at the top node. All members are modeled
as pin-connected truss elements (no bending moment resistance).

Key Steps:
----------
- Define a 3D FE model (FEModel3D) per frame.
- Add nodes and members based on geometry.
- Assign material and section properties.
- Apply support constraints (fixed and roller supports).
- Apply load at the top node (e.g., vertical downward force).
- Solve the system and extract:
    - Axial stresses in each member
    - Vertical deflection of the top node
    - Total structural mass (via Frame class)

Constraints:
------------
- Stress: must be below yield stress (250 MPa for steel)
- Deflection: vertical top node deflection ≤ 0.1 m

This module is called by the genetic optimizer to evaluate candidate frames.
"""
from Pynite import FEModel3D # type: ignore
from Pynite.FEModel3D import FEModel3D # type: ignore
import math
from frame import E, G, nu, density, yield_stress

# Use the same material properties defined in frame.py
from frame import E, G, nu, density, yield_stress

# Define allowable deflection (e.g., maximum vertical deflection at top node)
max_deflection = 0.1  # meters (example limit)

def analyze_frame(frame):
    """Run FEA on the given frame using PyNite and return mass, max_stress, max_deflection."""
    # Create a new 3D finite element model instance
    model = FEModel3D()

    # Add steel material (Young's modulus, shear modulus, Poisson's ratio, density)
    model.add_material('Steel', E, G, nu, density)

    # Define helper to add square cross-section approximations based on area
    def add_section(name, area):
        side = (area ** 0.5)            # Square section side length
        I = (side ** 4) / 12.0          # Moment of inertia (square cross-section)
        J = 2 * I                       # Approximate torsional constant
        model.add_section(name, area, I, I, J)

    # Assign sections to members
    add_section('LeftSec', frame.area_left)
    add_section('RightSec', frame.area_right)
    add_section('BaseSec', frame.area_base)

    # Add nodes to the model
    for node_name, coord in frame.nodes.items():
        x, y, z = coord
        model.add_node(node_name, x, y, z)

    # Support conditions:
    # Left support: fixed X, Y, Z translations; free rotation about Z (in-plane), fix rotations about X,Y (out-of-plane)
    model.def_support('N_left', True, True, True, True, True, True)
    # Right support: fixed Y, Z translations; free X translation (roller); fix out-of-plane rotations; free in-plane rot
    model.def_support('N_right', False, True, True, True, True, True)
    # Top node is free (but out-of-plane motions are inherently constrained by supports and member connectivity)

    model.def_support('N_top', False, False, False, False, False, True)
    # Add truss-like members (pin-jointed via moment releases)
    model.add_member('M_left',  'N_left',  'N_top', 'Steel', 'LeftSec')
    model.add_member('M_right', 'N_right', 'N_top', 'Steel', 'RightSec')
    model.add_member('M_base',  'N_left',  'N_right', 'Steel', 'BaseSec')

    # Simulate truss behavior: release moments at both ends of each member
    for m in ['M_left', 'M_right', 'M_base']:
        model.def_releases(m, Rzi=True, Rzj=True)

    # Apply external load: downward force at the top node
    load_value = 100000.0  # N (~10 tons)
    model.add_node_load('N_top', 'FY', -load_value)

    # Solve the model
    model.analyze()

    # Extract support reactions for force recovery (static analysis)
    Rxn_left_X = model.nodes['N_left'].RxnFX['Combo 1']
    Rxn_left_Y = model.nodes['N_left'].RxnFY['Combo 1']
    Rxn_right_Y = model.nodes['N_right'].RxnFY['Combo 1']

    # Use equilibrium to compute axial forces in each member
    base_axial = abs(Rxn_left_X)  # Base tie force
    left_leg_axial = math.sqrt(Rxn_left_Y**2 + Rxn_left_X**2)
    right_leg_axial = math.sqrt(Rxn_right_Y**2 + Rxn_left_X**2)

    # Axial stresses = force / area
    stress_left = abs(left_leg_axial) / frame.area_left
    stress_right = abs(right_leg_axial) / frame.area_right
    stress_base = abs(base_axial) / frame.area_base
    max_stress = max(stress_left, stress_right, stress_base)

    # Get vertical deflection of the top node
    top_deflection = abs(model.nodes['N_top'].DY['Combo 1'])

    # Calculate frame mass
    mass = frame.calc_mass()

    return mass, max_stress, top_deflection
