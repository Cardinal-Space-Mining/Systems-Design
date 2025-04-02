import numpy as np
import matplotlib.pyplot as plt

#all units are SI

class Frame():
    """
    Custom class to hold all information about the frame structure.
    Analysis and update functionality will be added as methods.
    """
    def __init__(self):
        """
        Goal: define initial frame design
        +X is forward, +Y is left, +Z is up (right hand rule)
        Therefore, mirroring means flipping the sign of the Y coordinate

        Nodes are divided into reaction nodes, load nodes, intermediate nodes, and symmetry nodes.
        We start by defining the left side, then mirroring all nodes except the symmetry nodes.
        Each type except symmetry has both a right and left dictionary. In the "right" dictionary, a string will be appended to the key to
        differentiate it.
        Symmetry nodes are locked to Y=0, but otherwise behave like intermediate nodes
        """

        #reaction nodes
        self.reaction_nodes_left = {"react1": [0.0, 0.28, 0.0], "react2": [0.4, 0.28, 0.0]}
        self.reaction_nodes_right = {}

        #mirror reaction nodes to get right side

    

        #load nodes
        self.load_nodes = {"PivotL": [-0.1, 0.26, 0.15], "ActuatorL": [0.3, 0.26, 0.05]}
        self.load_nodes["PivotR"] = self.load_nodes["PivotL"].copy()
        self.load_nodes["PivotR"][1] *= -1
        self.load_nodes["ActuatorR"] = self.load_nodes["ActuatorL"].copy()
        self.load_nodes["ActuatorR"][1] *= -1

        #intermediate nodes
        self.intermediate_nodes = {}            #empty for initial design, can be added later by "mutate topology" method

        self.symmetry_nodes = {}

        self.members = {}

        self._enforce_symmetry()


    def _enforce_symmetry(self):
        """
        Deletes all points in the "right" dictionaries and replaces them with mirrored copies of the points in the "left" dictionaries.
        Mirrors members, loads, and constraints as well in similar ways.
        Symmetry nodes are not mirrored, but are locked to Y=0.
        """
        self.reaction_nodes_right = {}
        for node in self.reaction_nodes_left:
            new_name = node + "R"
            self.reaction_nodes_right[new_name] = self.reaction_nodes_left[node].copy()
            self.reaction_nodes_right[new_name][1] *= -1


    def mutate_topology(self):
        """
        TODO: Mutate the topology of the frame by adding or removing intermediate nodes and members.
        """
        pass

    def mutate_shape(self):
        """
        TODO: Mutate the shape of the frame by adding noise to the coordinates of the intermediatenodes.
        """
        pass

    def _analyze_fea(self):
        """
        TODO: Analyze the frame structure to determine the max stress and .
        This will be done using a finite element analysis method.
        """
        pass

    def _check_interference(self):
        """
        Check for interference between the frame and the hopper/tracks/rock
        This will only conside members.
        The method will return a float indicating the amount of interference.
        """
        pass

    def reward_function(self):
        """
        Calculate the reward function based on the max stress, deflection, and interference.
        The reward function will be a weighted sum of these three values.
        """
        pass





if __name__ == "__main__":

    test_frame = Frame()

    print(test_frame.reaction_nodes_right)

    #plotting
    all_nodes = test_frame.reaction_nodes_right.copy() | test_frame.load_nodes.copy() | test_frame.intermediate_nodes.copy() | test_frame.symmetry_nodes.copy()
    xdata = []
    ydata = []
    zdata = []
    for node in all_nodes:                          #rearrange point data into lists for plotting
        xdata.append(all_nodes[node][0])
        ydata.append(all_nodes[node][1])
        zdata.append(all_nodes[node][2])

    plt.figure()
    ax = plt.axes(projection='3d')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.scatter3D(xdata, ydata, zdata)
    plt.show()
