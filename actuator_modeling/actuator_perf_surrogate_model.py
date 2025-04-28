# goal: estimate relationship between actuator torque, actuator rpm, and actuator mass based on existing data
# by "actuator" we mean a motor + gearbox + motor controller
# the goal is a polynomial for mass in terms of torque and speed

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.optimize import curve_fit


# step 1: load data from csv file (originally on Teams)

raw_data = pd.read_csv("actuator_modeling/commercial_actuator_data.csv",
                 usecols=['SKU', 'Rated Torque', 'Rated Speed', 'total weight'])
#remove rows with NaN values
raw_data = raw_data.dropna()

# step 2: construct pareto front of existing data
#         i. e. loop over the data. For each point, check if it it dominated by another point by looping over all other data
#         If there exists another point that has a higher torque, higher speed, and lower mass, remove the first point

pareto_front = raw_data.copy()

for i, actuator_candidate in raw_data.iterrows():
    for j, actuator_comparison in raw_data.iterrows():
        if i != j:
            # check if actuator_candidate is dominated by actuator_comparison
            if (actuator_candidate['Rated Torque'] < actuator_comparison['Rated Torque'] and
                actuator_candidate['Rated Speed'] < actuator_comparison['Rated Speed'] and
                actuator_candidate['total weight'] > actuator_comparison['total weight']):

                # remove actuator_candidate from the list of candidates
                pareto_front = pareto_front.drop(i)
                break


#plot pareto front data

skus = pareto_front['SKU'].to_list()
torques = pareto_front['Rated Torque'].to_list()
speeds = pareto_front['Rated Speed'].to_list()
masses = pareto_front['total weight'].to_list()


fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(projection='3d')
ax.scatter(torques, speeds, masses, c='blue', marker='o', s=20, label='All Data')


 

# select the validation subsets
validation_subset_fraction = 0.2
validation_subsets = 10
sample_size = int(len(skus))

validation_subset_size = int(sample_size * validation_subset_fraction)

validation_torques = [[] for _ in range(validation_subsets)]
validation_speeds = [[] for _ in range(validation_subsets)]
validation_masses = [[] for _ in range(validation_subsets)]

training_torques = [[] for _ in range(validation_subsets)]
training_speeds = [[] for _ in range(validation_subsets)]
training_masses = [[] for _ in range(validation_subsets)]

for i in range(validation_subsets):
    sampling_order = [i for i in range(sample_size)]
    random.shuffle(sampling_order)

    # construct validation subset
    for j in range(0, validation_subset_size):
        
        random_index = sampling_order[j]

        validation_torques[i].append(torques[random_index])
        validation_speeds[i].append(speeds[random_index])
        validation_masses[i].append(masses[random_index])

    # construct the training subset
    for j in range(validation_subset_size, sample_size):
        
        random_index = sampling_order[j]

        training_torques[i].append(torques[random_index])
        training_speeds[i].append(speeds[random_index])
        training_masses[i].append(masses[random_index])






# step 3: fit an n-degree polynomial to the pareto front data

def n_degree_polynomial(X, *weights):
    """
    Polynomial function of variable degree for curve fitting.
    """
    torque, speed = X
    degree = int((len(weights) ** 0.5) - 1)  # Infer degree from the number of weights

    function_value = 0.0
    weight_index = 0
    for i in range(degree + 1):
        for j in range(degree + 1):
            function_value += weights[weight_index] * (torque ** i) * (speed ** j)
            weight_index += 1

    return function_value



# Perform cross validation to determine best polynomial degree

max_polynomial_degree = 5  # Maximum degree of polynomial to fit

cross_valid_SSEs = [[] for _ in range(1, max_polynomial_degree)]

for degree in range(1, max_polynomial_degree):

    for subset_index in range(validation_subsets):

        # Dynamically calculate the number of weights based on the degree
        num_weights = (degree + 1) ** 2
        initial_weights = [0.1] * num_weights  # Initial guess for weights

        # Fit the curve only using the training subset

        fit = curve_fit(
            n_degree_polynomial,
            (training_torques[subset_index], training_speeds[subset_index]),
            training_masses[subset_index],
            p0=initial_weights,
            maxfev=10000
        )

        fitted_weights = fit[0]


        # find the SSE with respect to the corresponding validation subset
        subset_SSE = 0.0

        for k in range(len(validation_torques[subset_index])):
            test_point = (validation_torques[subset_index][k], validation_speeds[subset_index][k])
            fit_value = n_degree_polynomial(test_point, *fitted_weights)
            subset_SSE += (validation_masses[subset_index][k] - fit_value) ** 2
        
        cross_valid_SSEs[degree - 1].append(subset_SSE)

print("Cross-validation SSEs:")
print(np.array(cross_valid_SSEs))


# build a model using all of the data and a specified degree
degree = 4          #should be manually set based on the results of the above cross-validation
num_weights = (degree + 1) ** 2
initial_weights = [0.1] * num_weights  # Initial guess for weights

# Fit the curve
fit = curve_fit(
    n_degree_polynomial,
    (torques, speeds),
    masses,
    p0=initial_weights,
    maxfev=10000
)

fitted_weights = fit[0]



# Plot the fitted polynomial

x = np.linspace(0, 130, 30)
y = np.linspace(0, 650, 30)
  
X, Y = np.meshgrid(x, y)
Z = np.zeros(X.shape)

for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        Z[i, j] = n_degree_polynomial((X[i, j], Y[i, j]), *fitted_weights)

for i in range(len(Z)):
    for j in range(len(Z[i])):
        if Z[i][j] > 3:
            Z[i][j] = 3
        if Z[i][j] < 0:
            Z[i][j] = 0

ax.plot_wireframe(X, Y, Z, color ='green')
ax.set_xlabel("Torque (Nm)")
ax.set_ylabel("Speed (rpm)")
ax.set_zlabel("Mass")
plt.show()




