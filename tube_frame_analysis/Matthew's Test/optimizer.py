# optimizer.py
"""
Genetic Algorithm for Frame Weight Minimization
===============================================

This module implements a Genetic Algorithm (GA) to optimize a triangular truss frame
subject to structural constraints. The goal is to minimize the total mass of the frame
while ensuring that the axial stress in any member does not exceed the material yield
stress, and the deflection of the top node stays within a specified limit.

Key Algorithm Steps:
--------------------
1. Initialize a population of random frames (designs).
2. Evaluate each frame via FEA (mass, max stress, deflection).
3. Assign fitness = mass + penalties (if constraints are violated).
4. Rank frames by fitness (lower is better).
5. Select top-performing frames as parents.
6. Apply crossover and mutation to generate offspring.
7. Repeat for a fixed number of generations.

Constraint Handling:
--------------------
- Penalty terms added to fitness if max stress > yield_stress or
  if max deflection > allowed deflection.
- Weighting factor amplifies the penalty to bias GA toward feasible designs.

Advantages:
-----------
- No need for derivatives or gradients.
- Can handle nonlinear, discontinuous design spaces.
- Easy to extend for more complex topologies, materials, or constraints.

Used with: frame.py (Frame geometry) and fea_solver.py (FEA analysis)
"""
import random
import math
from matplotlib import pyplot as plt
from frame import Frame
from fea_solver import analyze_frame, yield_stress, max_deflection

def optimize_frame(pop_size=20, generations=50):
    """Genetic algorithm to minimize frame mass under stress/deflection constraints."""

    # Step 1: Initialize population with random frames
    population = [Frame.random_frame() for _ in range(pop_size)]
    best_frame = None
    best_fitness = float('inf')

    # Evolution loop
    for gen in range(generations):
        fitness_scores = []

        # Step 2: Evaluate each frame's performance
        for frame in population:
            mass, max_stress, max_defl = analyze_frame(frame)

            # Step 3: Compute fitness score (base = mass, add penalties)
            fitness = mass

            if max_stress > yield_stress:
                # Stress constraint violation penalty
                fitness += mass * 10 * ((max_stress / yield_stress) - 1)

            if max_defl > max_deflection:
                # Deflection constraint violation penalty
                fitness += mass * 10 * ((max_defl / max_deflection) - 1)

            fitness_scores.append((fitness, frame, mass, max_stress, max_defl))

        # Step 4: Rank by fitness
        fitness_scores.sort(key=lambda x: x[0])  # lower fitness = better

        # Update best frame found so far
        best_current = fitness_scores[0]
        if best_current[0] < best_fitness:
            best_fitness = best_current[0]
            best_frame = best_current[1]
            print(f"Generation {gen}: Best mass = {best_current[2]:.2f} kg, "
                  f"Max stress = {best_current[3]:.1f} Pa, Max defl = {best_current[4]:.3f} m")
            
            # Plot the frame
            fig, ax = plt.subplots()
            nodes = best_current[1].nodes
            members = best_current[1].members
            for n1, n2, _ in members:
                x_vals = [nodes[n1][0], nodes[n2][0]]
                y_vals = [nodes[n1][1], nodes[n2][1]]
                ax.plot(x_vals, y_vals, 'bo-', linewidth=2)
            ax.set_title(f"Generation {gen}")
            ax.set_aspect('equal')
            ax.set_xlabel("X (m)")
            ax.set_ylabel("Y (m)")
            plt.grid(True)
            plt.show(block=False)
            plt.pause(0.1)
            plt.close()

        # Step 5: Selection (top 50% as parents)
        num_parents = pop_size // 2
        parents = [fs[1] for fs in fitness_scores[:num_parents]]

        # Step 6: Reproduce new population
        new_pop = []
        # Elitism: keep top 2 frames unchanged
        new_pop.append(fitness_scores[0][1])
        new_pop.append(fitness_scores[1][1])

        # Generate offspring via crossover and mutation
        while len(new_pop) < pop_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            # Crossover: randomly inherit each design variable
            child_width = random.choice([parent1.width, parent2.width])
            child_height = random.choice([parent1.height, parent2.height])
            child_area_left = random.choice([parent1.area_left, parent2.area_left])
            child_area_right = random.choice([parent1.area_right, parent2.area_right])
            child_area_base = random.choice([parent1.area_base, parent2.area_base])

            child = Frame(child_width, child_height, child_area_left, child_area_right, child_area_base)
            child.mutate(mutation_rate=0.1)  # Mutate child design
            new_pop.append(child)

        # Step 7: Update population
        population = new_pop

    return best_frame

# Example usage when run as script
if __name__ == "__main__":
    best = optimize_frame(pop_size=30, generations=100)
    print("Best frame found:", best)
    
    # Evaluate best frame performance
    mass, max_stress, max_defl = analyze_frame(best)


    print(f"Mass = {mass:.2f} kg")
    print(f"Max stress = {max_stress/1e6:.2f} MPa (Yield stress = {yield_stress/1e6:.0f} MPa)")
    print(f"Max deflection = {max_defl*1000:.2f} mm (Limit = {max_deflection*1000:.0f} mm)")

    # Visualization of the frame
    fig, ax = plt.subplots()
    nodes = best.nodes
    members = best.members
    for n1, n2, _ in members:
        x_values = [nodes[n1][0], nodes[n2][0]]
        y_values = [nodes[n1][1], nodes[n2][1]]
        ax.plot(x_values, y_values, 'bo-', linewidth=2)

    ax.set_aspect('equal')
    ax.set_title("Optimal Frame Geometry")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    plt.grid(True)
    plt.savefig("optimal_frame.png")