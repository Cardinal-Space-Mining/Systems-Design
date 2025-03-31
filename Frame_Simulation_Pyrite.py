from Pynite import FEModel3D
import numpy as np
import math




"""
Overall goal: calculate the max stress and max deformation of a robot frame structure under a given loading condition(s)
Wrap this in a function that can be called with different parameters for different frame designs, which will be used in a component in an OpenMDAO optimizer.

Take in the lists of reaction, load, and intermediate nodes, along with the applied loads/boundary conditions for each case,
and the list of member connections.
Output the maximum global stress, and the maximum deformation for a given node (which node can be hardcoded)


Use Pynite to assemble a finite element model of the frame structure, and solve deformations.
Then test many points along each member's length and surface to find the local stress. Make sure these points are evenly distributed.
Store each local stress in a list, sort the list, and pull out the final element for max stress

Directly pull out deflections from the node of interest.


"""
def section_properties(shape, *args):
    
    #returns tuple of section properties in order of Iy, Iz, J, A
    
    if shape == "tube":
        OD = args[0]
        ID = args[1]
        Iy = Iz = math.pi*(1/64)*(OD**4 - ID**4)
        J = 2*Iy
        A = math.pi*(1/4)*(OD**2 - ID**2)

        return Iy, Iz, J, A
    
    if shape == "box":
        width_outer = W = args[0]
        width_inner = w1 = args[1]
        height_inner = H = args[2]
        height_inner = h1 = args[3]
        pass
        
        

def shear_constants(shape, distance_from_centroid, *args):

    #returns an array of Q and b for a given distance from centroidal axis

    if shape == "tube":
        OD = args[0]
        ID = args[1]
        Outer_radius = OD/2
        Inner_radius = ID/2

        Q = 1
        b = 1

        return Q, b
    
    if shape == "box":
        pass

    

#start with initial frame design, regolith load, mining load, and twisting load
reaction_nodes = []
# note that these load cases have different supports
#build frame
#build load cases

#solve FEA

#unpack forces for each member at various points along the span
# Test all points on cross section
# for each test point, find principle stresses


def find_stress_on_tube(location, load_list, section_properties, OD, ID):
    
    # assume circular cross section
    # "location" is a 3D vector respresenting the point of stress in member-space
    y_pos = location[1]
    z_pos = location[2]

    Iy = Iz = section_properties[0]
    J = section_properties[2]
    A = section_properties[3]

    Fx, Fy, Fz = load_list[0], load_list[1], load_list[2]           #internal forces at the point of interest
    Mx, My, Mz = load_list[3], load_list[4], load_list[5]           #internal moments at the point of interest
    
    Qz, bz = shear_constants("tube", z_pos, OD, ID)
    Qy, by = shear_constants("tube", y_pos, OD, ID)


    axial_stress = (Fx/A) + (My*z_pos/Iy) - (Mz*y_pos/Iz)
    shear_stress_z = (Fz*Qz)/(Iz*bz)

    
    
    #axial stress
    #shear y
    #shear z 

#find max deformation of load application points, max global deformation, and max global stress