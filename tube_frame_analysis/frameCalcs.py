import math

def frameMass(density: float, geometry: list) -> float:
    mass = 0.0
    for element in geometry:
        outerDiameter, thickness, length = element
        volume = math.pi*length*((outerDiameter**2) - ((outerDiameter - thickness)**2))
        mass += density*volume
    return mass



aluminum_6061_density = 2720 #kg/m^3

geometry = [[.04, .002, .3],
            [.05, .002, .8],
            [.03, .006, .9],
            [.02, .002, .3],
            [.04, .004, .4],]

test_mass = frameMass(aluminum_6061_density, geometry)
print(f"The mass of the frame is {test_mass} kg")

