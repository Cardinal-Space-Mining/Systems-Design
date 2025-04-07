import random
import math

from matplotlib import pyplot as plt
from frame import Frame
from fea_solver import analyze_frame, yield_stress, max_deflection

def optimize_frame(pop_size=20, generations=50):
    """Genetic algorithm to minimize frame mass under stress/deflection constraints."""
    # Initialize population with random frames
    population = [Frame.random_frame() for _ in range(pop_size)]
    best_frame = None
    best_fitness = float('inf')
    # Evolution loop
    for gen in range(generations):
        # Evaluate fitness of each frame in the population
        fitness_scores = []
        for frame in population:
            mass, max_stress, max_defl = analyze_frame(frame)
            # Calculate fitness (mass with penalties for constraint violations)
            fitness = mass
            # Penalize stress constraint violation
            if max_stress > yield_stress:
                # add penalty proportional to the excess stress ratio
                fitness += mass * 10 * ((max_stress / yield_stress) - 1)
            # Penalize deflection constraint violation
            if max_defl > max_deflection:
                fitness += mass * 10 * ((max_defl / max_deflection) - 1)
            fitness_scores.append((fitness, frame, mass, max_stress, max_defl))
        # Sort by fitness (lower is better)
        fitness_scores.sort(key=lambda x: x[0])
        # Keep track of the best frame found
        best_current = fitness_scores[0]
        if best_current[0] < best_fitness:
            best_fitness = best_current[0]
            best_frame = best_current[1]
            # Optionally, print progress
            print(f"Generation {gen}: Best mass = {best_current[2]:.2f} kg, "
                  f"Max stress = {best_current[3]:.1f} Pa, Max defl = {best_current[4]:.3f} m")
            
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
        # Selection: take top half of population as parents
        num_parents = pop_size // 2
        parents = [fs[1] for fs in fitness_scores[:num_parents]]
        # Reproduce new population
        new_pop = []
        # Elitism: carry over a couple of best designs without change
        new_pop.append(best_current[1])  # best frame
        new_pop.append(fitness_scores[1][1])  # second best frame
        # Fill the rest of the new population
        while len(new_pop) < pop_size:
            # Pick two parents (could use tournament or random selection weighted by fitness)
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            # Crossover: mix parent genes (design variables)
            child_width = random.choice([parent1.width, parent2.width])
            child_height = random.choice([parent1.height, parent2.height])
            child_area_left = random.choice([parent1.area_left, parent2.area_left])
            child_area_right = random.choice([parent1.area_right, parent2.area_right])
            child_area_base = random.choice([parent1.area_base, parent2.area_base])
            child = Frame(child_width, child_height, child_area_left, child_area_right, child_area_base)
            # Mutation
            child.mutate(mutation_rate=0.1)
            new_pop.append(child)
        # Prepare for next generation
        population = new_pop
    return best_frame

# If run as script, execute optimization
if __name__ == "__main__":
    best = optimize_frame(pop_size=30, generations=100)
    print("Best frame found:", best)
    # Evaluate best frame performance
    mass, max_stress, max_defl = analyze_frame(best)
    print(f"Mass = {mass:.2f} kg, Max Stress = {max_stress:.1f} Pa, Max Deflection = {max_defl:.3f} m")

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
    plt.show()