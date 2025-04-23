# goal: estimate relationship between actuator torque, actuator rpm, and actuator mass based on existing data
# by "actuator" we mean a motor + gearbox + motor controller
# the goal is a polynomial for mass in terms of torque and speed

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om
import random


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

"""
fig = plt.figure(figsize=(8, 7))
ax = fig.add_subplot(projection='3d')
ax.scatter(torques, speeds, masses, c='blue', marker='o', s=20, label='All Data')
plt.show()


"""

# select the validation subsets
validation_subset_fraction = 0.2
validation_subsets = 5
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

        # append the corresponding data to the validation subset
        validation_torques[i].append(torques[random_index])
        validation_speeds[i].append(speeds[random_index])
        validation_masses[i].append(masses[random_index])

    # construct the training subset
    for j in range(validation_subset_size, sample_size):
        
        random_index = sampling_order[j]

        # append the corresponding data to the training subset
        training_torques[i].append(torques[random_index])
        training_speeds[i].append(speeds[random_index])
        training_masses[i].append(masses[random_index])





# step 3: fit an n-degree polynomial to the pareto front data

max_polynomial_degree = 5

class PolynomialSSE(om.ExplicitComponent):
    def setup(self):
        self.add_input('torques', val=np.zeros(len(torques)))
        self.add_input('speeds', val=np.zeros(len(speeds)))
        self.add_input('masses', val=np.zeros(len(masses)))

        self.add_input('degree', val=0)
        self.add_input('weights', val= 100 * np.ones((3, 3)))

        self.add_output('SSE', val=0.0)
        self.add_output('fitted_masses', val=np.zeros(len(masses)))

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd', step=1e-10)
    
    def compute(self, inputs, outputs):
        weights = inputs['weights']
        degree = inputs['degree']

        torques = inputs['torques']
        speeds = inputs['speeds']
        masses = inputs['masses']

        SSE = 0.0
        fitted_masses = np.zeros(len(masses))

        for k, mass in enumerate(masses):
            curve_val = 0.0
            for i in range(int(degree[0]) + 1):
                for j in range(int(degree[0]) + 1):
                    curve_val += (weights[j,i]) * (torques[k]**i) * (speeds[k]**j)
                    fitted_masses[k] = curve_val
                    SSE += (curve_val - mass)**2

        outputs['SSE'] = SSE
        outputs['fitted_masses'] = fitted_masses




model = om.Group()
model.add_subsystem('fittedSSE', PolynomialSSE(), promotes=['*'])

prob = om.Problem(model)

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['optimizer'] = 'SLSQP'

prob.model.add_design_var('weights')
prob.model.add_objective('SSE')

prob.setup()

prob.set_val('torques', torques)
prob.set_val('speeds', speeds)
prob.set_val('masses', masses)
prob.set_val('degree', 2)




prob.run_driver()

weights = prob.get_val("weights")
final_SSE = prob.get_val("SSE")

print(f"final SSE: {final_SSE}")

print(f"weights:")
print(weights)





# step 4: perform k-fold cross validation to determine the best polynomial degree

# step 5: retrain the model with the best polynomial degree on the entire dataset


