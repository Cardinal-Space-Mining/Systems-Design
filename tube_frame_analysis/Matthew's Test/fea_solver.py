from Pynite import FEModel3D
from Pynite.FEModel3D import FEModel3D
import math

# Use the same material properties defined in frame.py
from frame import E, G, nu, density, yield_stress

# Define allowable deflection (e.g., maximum vertical deflection at top node)
max_deflection = 0.1  # meters (example limit)

def analyze_frame(frame):
    """Run FEA on the given frame using PyNite and return mass, max_stress, max_deflection."""
    # Create a new 3D finite element model
    model = FEModel3D()
    # Add material (if not already added, ensure unique name or reuse)
    model.add_material('Steel', E, G, nu, density)
    # Define cross-section properties for each member (assuming square section for moment of inertia calc)
    def add_section(name, area):
        side = (area ** 0.5)  # treat as square side length
        I = (side ** 4) / 12.0  # moment of inertia for a square cross-section
        J = 2 * I               # torsional constant (approx.)
        model.add_section(name, area, I, I, J)
    add_section('LeftSec', frame.area_left)
    add_section('RightSec', frame.area_right)
    add_section('BaseSec', frame.area_base)
    # Add nodes to the model
    for node_name, coord in frame.nodes.items():
        x, y, z = coord
        model.add_node(node_name, x, y, z)
    # Define supports (fixed translations at base nodes; one base node free in X for stability)
    # Left support: fixed X, Y, Z translations; free rotation about Z (in-plane), fix rotations about X,Y (out-of-plane)
    model.def_support('N_left', True, True, True, True, True, True)
    # Right support: fixed Y, Z translations; free X translation (roller); fix out-of-plane rotations; free in-plane rot
    model.def_support('N_right', False, True, True, True, True, True)
    # Restrain in-plane rotation at the top node
    model.def_support('N_top', False, False, False, False, False, True)
    # The top node is free (but out-of-plane motions are inherently constrained by supports and member connectivity)
    # Add frame members
    model.add_member('M_left',  'N_left',  'N_top', 'Steel', 'LeftSec')
    model.add_member('M_right', 'N_right','N_top', 'Steel', 'RightSec')
    model.add_member('M_base',  'N_left',  'N_right','Steel','BaseSec')
    # Apply pin (hinge) releases at member ends to simulate truss behavior [oai_citation_attribution:2‡pynite.readthedocs.io](https://pynite.readthedocs.io/en/stable/member.html#:~:text=End%20releases%20can%20be%20applied,way%20truss%20members)
    for m in ['M_left', 'M_right', 'M_base']:
        # Release moments (local z rotations) at both i and j ends
        model.def_releases(m, Rzi=True, Rzj=True)
    # Apply external load (e.g., downward force at top node)
    load_value = 100000.0  # N (e.g., ~10 ton load)
    model.add_node_load('N_top', 'FY', -load_value)
    
    # Solve the model
    model.analyze()
    # Extract support reactions for internal forces
    # (Using default load combination 'Combo 1')
    Rxn_left_X = model.nodes['N_left'].RxnFX['Combo 1']
    Rxn_left_Y = model.nodes['N_left'].RxnFY['Combo 1']
    Rxn_right_Y = model.nodes['N_right'].RxnFY['Combo 1']
    # Compute member axial forces from equilibrium (with pin connections):
    # Base member force = horizontal reaction at left support
    base_axial = abs(Rxn_left_X)
    # Left/right leg axial forces (from vertical reaction and base tie force)
    left_leg_axial = math.sqrt(Rxn_left_Y**2 + Rxn_left_X**2)
    right_leg_axial = math.sqrt(Rxn_right_Y**2 + Rxn_left_X**2)
    # Compute stresses in each member (force / area)
    stress_left = abs(left_leg_axial) / frame.area_left
    stress_right = abs(right_leg_axial) / frame.area_right
    stress_base = abs(base_axial) / frame.area_base
    max_stress = max(stress_left, stress_right, stress_base)
    # Get deflection at the top node (global Y direction)
    top_deflection = abs(model.nodes['N_top'].DY['Combo 1'])
    # Get frame mass from its geometry
    mass = frame.calc_mass()
    return mass, max_stress, top_deflection