from frame import Frame
from frame import yield_stress
from optimizer import optimize_frame
from fea_solver import analyze_frame
from fea_solver import max_deflection
import matplotlib.pyplot as plt

best_frame = optimize_frame(pop_size=30, generations=100)
print("Optimal frame design:", best_frame)
mass, max_stress, max_defl = analyze_frame(best_frame)
print(f"Mass = {mass:.2f} kg")
print(f"Max stress = {max_stress/1e6:.2f} MPa (Yield stress = {yield_stress/1e6:.0f} MPa)")
print(f"Max deflection = {max_defl*1000:.2f} mm (Limit = {max_deflection*1000:.0f} mm)")

# Visualization of the frame
fig, ax = plt.subplots()
nodes = best_frame.nodes
members = best_frame.members
for n1, n2, _ in members:
    x_values = [nodes[n1][0], nodes[n2][0]]
    y_values = [nodes[n1][1], nodes[n2][1]]
    ax.plot(x_values, y_values, 'bo-', linewidth=2)

ax.set_aspect('equal')
ax.set_title("Optimal Frame Geometry")
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
plt.grid(True)
plt.show()