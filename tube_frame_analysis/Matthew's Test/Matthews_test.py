# from Pynite import FEModel3D
# from Pynite.Rendering import Renderer
# import numpy as np
# import math
# from scipy.optimize import minimize

# # ========================== USER INPUT SECTION ==========================
# # Robot dimensions
# robotWidth = 0.400   # Width of the frame in meters
# robotLength = 0.600  # Length of the frame in meters

# # Material Properties (Steel Example)
# E = 200e9            # Young's modulus (Pa)
# nu = 0.3             # Poisson's ratio
# G = E / (2 * (1 + nu))  # Shear modulus
# density = 7850       # Density (kg/m³)
# yield_strength = 250e6  # Yield Strength (Pa)

# # Load Conditions
# force_N2 = -10000  # Force applied at node N2 (N)
# force_N3 = -10000  # Force applied at node N3 (N)

# # Design Constraints
# OD_bounds = (0.02, 0.1)  # Outer diameter bounds (m)
# ID_ratio = 0.8  # Inner diameter as a fraction of outer diameter
# initial_OD = 0.05  # Initial guess for outer diameter (m)

# # =======================================================================

# def section_properties(shape, *args):
#     """Returns section properties: Iy, Iz, J, A"""
#     if shape == "tube":
#         OD, ID = args
#         Iy = Iz = (math.pi / 64) * (OD**4 - ID**4)
#         J = (math.pi / 32) * (OD**4 - ID**4)
#         A = (math.pi / 4) * (OD**2 - ID**2)
#         return Iy, Iz, J, A
#     elif shape == "box":
#         W, w1, H, h1 = args
#         Iy = (1/12) * (W * H**3 - w1 * h1**3)
#         Iz = (1/12) * (H * W**3 - h1 * w1**3)
#         J = (2/3) * ((W * H - w1 * h1) * (W * H + w1 * h1)) / (W / H + H / W)
#         A = (W * H) - (w1 * h1)
#         return Iy, Iz, J, A
#     return None, None, None, None

# def shear_constants(shape, distance_from_centroid, *args):
#     """Returns shear stress parameters [Q, b]"""
#     if shape == "tube":
#         OD, ID = args
#         A_prime = (math.pi / 2) * ((OD / 2)**2 - (ID / 2)**2)
#         Q = A_prime * distance_from_centroid
#         b = math.pi * (OD - ID)
#         return Q, b
#     elif shape == "box":
#         W, w1, H, h1 = args
#         Q = ((W * H - w1 * h1) / 2) * distance_from_centroid
#         b = 2 * (W + H - w1 - h1)
#         return Q, b
#     return None, None

# # Stress Calculation
# def find_stress_on_tube(location, load_list, section_properties, OD, ID):
#     """Calculates axial, shear, and torsional stress"""
#     y_pos, z_pos = location[1], location[2]
#     Iy, Iz, J, A = section_properties
#     Fx, Fy, Fz, Mx, My, Mz = load_list
#     Qz, bz = shear_constants("tube", z_pos, OD, ID)
#     Qy, by = shear_constants("tube", y_pos, OD, ID)
    
#     axial_stress = (Fx / A) + (My * z_pos / Iy) - (Mz * y_pos / Iz)
#     shear_stress_z = (Fz * Qz) / (Iz * bz)
#     shear_stress_y = (Fy * Qy) / (Iy * by)
#     torsional_stress = (Mx * (OD / 2)) / J

#     return axial_stress, shear_stress_y, shear_stress_z, torsional_stress

# # ========================== FEA MODEL CREATION ==========================
# def create_FEA_model(OD, ID):
#     """Creates and solves the finite element model"""
#     frame = FEModel3D()

#     # Define nodes
#     frame.add_node("N1", 0, 0, 0)
#     frame.add_node("N2", robotWidth, 0, 0)
#     frame.add_node("N3", robotWidth, 0, robotLength)
#     frame.add_node("N4", 0, 0, robotLength)

#     # Define material
#     frame.add_material("Steel", E, G, 0.3, density)

#     # Define section
#     Iy, Iz, J, A = section_properties("tube", OD, ID)
#     if None in (Iy, Iz, J, A):
#         raise ValueError("Invalid section properties")

#     frame.add_section("Tube_Section", A, Iy, Iz, J)

#     # Define members
#     frame.add_member("M1", "N1", "N2", "Steel", "Tube_Section")
#     frame.add_member("M2", "N2", "N3", "Steel", "Tube_Section")
#     frame.add_member("M3", "N3", "N4", "Steel", "Tube_Section")
#     frame.add_member("M4", "N4", "N1", "Steel", "Tube_Section")

#     # Define supports
#     frame.def_support("N1", True, True, True, True, True, True)
#     frame.def_support("N4", True, True, True, True, True, True)

#     # Apply loads
#     frame.add_node_load("N2", "FY", force_N2)
#     frame.add_node_load("N3", "FY", force_N3)
#     frame.add_node_load("N2", "FX", force_N2)

#     # Solve FEA
#     frame.analyze()

#     # Extract max displacement
#     max_disp = max(abs(frame.nodes[node].DY["Combo 1"]) for node in frame.nodes)

#     # Extract max stress
#     max_force = max(abs(frame.members[m].max_axial()) for m in frame.members)

#     max_shear = max(abs(frame.members[m].max_shear()) for m in frame.members)

#     max_moment = max(abs(frame.members[m].max_moment()) for m in frame.members)


#     return frame, max_disp, max_force, max_shear, max_moment

# # ========================== OBJECTIVE FUNCTION ==========================
# def objective(OD):
#     """Objective: Minimize weight while ensuring stress constraints"""
#     ID = OD * ID_ratio  # Inner diameter as a fraction of OD
#     try:
#         frame, max_disp, max_force, max_shear, max_moment = create_FEA_model(OD, ID)
#     except ValueError:
#         return float('inf')

#     # Compute total mass of frame
#     frame_length = 2 * (robotWidth + robotLength)
#     mass = (math.pi * ((OD/2)**2 - (ID/2)**2) * frame_length * density)

#     # Penalize designs exceeding stress limits
#     if max_force > yield_strength:
#         return mass + 1e6  # Large penalty to avoid exceeding yield strength

#     return mass




# # ========================== RUN OPTIMIZATION ==========================
# print("\nRunning Optimization...\n")
# result = minimize(objective, x0=[initial_OD], bounds=[OD_bounds])
# optimized_OD = result.x[0]
# optimized_ID = optimized_OD * ID_ratio

# # ========================== FINAL ANALYSIS ==========================
# final_frame, max_deflection, max_force, max_shear, max_moment = create_FEA_model(optimized_OD, optimized_ID)

# # Compute final frame mass
# frame_length = 2 * (robotWidth + robotLength)
# final_mass = (math.pi * ((optimized_OD/2)**2 - (optimized_ID/2)**2) * frame_length * density)

# # ========================== PRINT RESULTS ==========================
# print("\n=== Optimization Results ===")
# print(f"Optimized Outer Diameter: {optimized_OD:.4f} m")
# print(f"Optimized Inner Diameter: {optimized_ID:.4f} m")
# print(f"Final Frame Mass: {final_mass:.2f} kg")
# print(f"Max Deflection: {max_deflection:.6f} m")
# print(f"Max Stress: {max_force:.2f} Pa")
# print(f"Yield Strength: {yield_strength:.2f} Pa")
# print(f"Stress Safety Factor: {yield_strength / max_force:.2f}")

# if max_force > yield_strength:
#     print("\nWARNING: Optimized design exceeds yield strength!")

# # ========================== VISUALIZATION ==========================
# renderer = Renderer(final_frame)
# renderer.annotation_size = 0.05
# renderer.render_loads = True
# renderer.render_model()